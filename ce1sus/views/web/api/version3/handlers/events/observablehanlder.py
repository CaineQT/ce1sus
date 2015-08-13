# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.classes.internal.object import Object
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableHandler(RestBaseHandler):

  def __init__(self, config):
    super(ObservableHandler, self).__init__(config)
    self.observable_controller = self.controller_factory(ObservableController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def observable(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      cache_object = self.get_cache_object(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      observable_id = requested_object.get('event_id')
      if observable_id:
        observable = self.observable_controller.get_observable_by_uuid(observable_id)
        event = self.observable_controller.get_event_for_observable(observable)
        # check if event is viewable by the current user
        self.check_if_event_is_viewable(event)
        self.set_event_properties_cache_object(cache_object, event)

        if requested_object['object_type'] is None:
          return self.__process_observable(method, event, observable, json, cache_object)
        elif requested_object['object_type'] == 'object':
          return self.__process_object(method, event, observable, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'observable':
          return self.__process_observable_child(method, event, observable, requested_object, json, cache_object)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Observable cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_observable_child(self, method, event, observable, requested_object, json, cache_object):
    if method == 'POST':
      self.check_if_user_can_add(event)
      child_obs = self.assembler.assemble(json, Observable, event, cache_object)
      child_obs.event = None
      child_obs.event_id = None
      if observable.observable_composition:
        observable.observable_composition.observables.append(child_obs)
        self.observable_controller.update_observable(observable, cache_object.user, True)
      else:
        # then it is a related observable
        pass
      return child_obs.to_dict(cache_object)
    else:
      raise RestHandlerException('use observable/{uuid} instead')

  def __process_observable(self, method, event, observable, json, cache_object):
    if method == 'POST':
      raise RestHandlerException('Recurive observables are currently not supported')
    else:
      self.check_item_is_viewable(event, observable)
      if method == 'GET':

        return observable.to_dict(cache_object)
      elif method == 'PUT':
        self.check_if_event_is_modifiable(event)
        self.check_if_user_can_set_validate_or_shared(event, observable, cache_object.user, json)
        observable = self.updater.update(observable, json, cache_object)
        self.observable_controller.update_observable(observable, cache_object.user, True)
        return observable.to_dict(cache_object)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_observable(observable, cache_object.user, True)
        return 'Deleted observable'

  def __set_properties(self, obj, cache_object, parent):
    obj.properties.is_rest_instert = cache_object.rest_insert
    obj.properties.is_web_insert = not cache_object.rest_insert
    if cache_object.owner:
      obj.properties.is_validated = True
      obj.properties.is_proposal = False
    else:
      obj.properties.is_validated = False
      obj.properties.is_proposal = True
    obj.properties.is_shareable = parent.properties.is_shareable

  def __process_object(self, method, event, observable, requested_object, json, cache_object):
    if method == 'POST':
      self.check_if_user_can_add(event)
      # check if observable has already an object
      if observable.object:
        # TODO: REVIEW THIS OBSERVABLE FOO -> idea is to create observable compositions out of objects if a second is added
        obs = Observable()
        obs.event = event
        obs.tlp_level_id = observable.tlp_level_id
        obs.parent = event
        self.observable_controller.set_extended_logging(obs, cache_object.user, True)
        self.__set_properties(obs, cache_object, observable)

        comp_obs = ObservableComposition()
        comp_obs.tlp = obs.tlp
        comp_obs.properties = obs.properties
        self.observable_controller.set_extended_logging(comp_obs, cache_object.user, True)

        comp_obs.parent = obs
        obs.observable_composition = comp_obs
        comp_obs.tlp_level_id = observable.tlp_level_id
        self.__set_properties(comp_obs, cache_object, observable)

        child_obs = Observable()
        child_obs.parent = event
        child_obs.tlp_level_id = observable.tlp_level_id
        comp_obs.observables.append(child_obs)
        comp_obs.observables.append(observable)

        self.__set_properties(child_obs, cache_object, observable)
        self.observable_controller.set_extended_logging(child_obs, cache_object.user, True)

        obj = self.assembler.assemble(json, Object, child_obs, cache_object)

        child_obs.object = obj
        self.observable_controller.insert_observable(obs, cache_object.user, True)
        observable.event = None
        observable.event_id = None

        self.observable_controller.insert_object(obj, cache_object.user, False)
        # update observable
        self.observable_controller.update_observable(observable, cache_object.user, True)
        cache_object.inflated = True
        return obs.to_dict(cache_object)
      else:
        obj = self.assembler.assemble(json, Object, observable, cache_object)
        self.observable_controller.insert_object(obj, True)
        return obj.to_dict(cache_object)
    else:
      uuid = requested_object['object_uuid']
      if uuid:
        obj = self.observable_controller.get_object_by_uuid(uuid)
        self.check_item_is_viewable(event, obj)
      else:
        if not cache_object.flat:
          raise PathParsingException(u'object cannot be called without an ID')
      if method == 'GET':
        if cache_object.flat:
          result = list()
          flat_objects = self.observable_controller.get_flat_observable_objects(observable)
          for flat_object in flat_objects:
            result.append(flat_object.to_dict(cache_object))
          return result
        else:
          return self.__process_object_get(requested_object, cache_object)
      elif method == 'PUT':
        self.check_if_event_is_modifiable(event)
        self.check_if_user_can_set_validate_or_shared(event, obj, cache_object.user, json)
        obj = self.updater.update(obj, json, cache_object)
        self.observable_controller.update_object(obj, cache_object.user, True)
        return obj.to_dict(cache_object)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_object(obj, cache_object.user, True)
        return 'Deleted observable'
