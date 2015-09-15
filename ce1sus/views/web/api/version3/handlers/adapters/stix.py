# -*- coding: utf-8 -*-

"""
(Description)

Created on 7 Sep 2015
"""
from base64 import b64decode
import cherrypy

from ce1sus.common.classes.cacheobject import MergerCache
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.handlers.base import HandlerException
from ce1sus.mappers.stix.ce1susstix import Ce1susSTIX
from ce1sus.mappers.stix.stixmapper import STIXConverter
from ce1sus.views.web.api.version3.handlers.adapters.base import AdapterHandlerBase
from ce1sus.views.web.api.version3.handlers.restbase import rest_method, methods, RestHandlerNotFoundException, RestHandlerException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class STIXHandler(AdapterHandlerBase):

  def __init__(self, config):
    super(STIXHandler, self).__init__(config)
    self.dump = self.adapter_config.get('STIXMapper', 'dump', False)
    self.dump_location = self.adapter_config.get('STIXMapper', 'path', False)
    self.stix_converter = STIXConverter(config)
    self.ce1sus_converter = Ce1susSTIX(config)

  @rest_method(default=True)
  @methods(allowed=['POST'])
  @require()
  def upload_xml(self, **args):
    try:
      cache_object = self.get_cache_object(args)
      cache_object.event_permissions = EventPermissions('0')
      cache_object.event_permissions.set_all()
      json = args.get('json')

      # check if the json is as expected
      filename = json.get('name', None)
      if filename:
        if 'XML' in filename or 'xml' in filename:
          data = json.get('data', None)
          if data:
            if data.get('data', None):
              data = data['data']
          else:
            raise HandlerException('Provided json does not have a data attribute')
        else:
          raise HandlerException('File does not end in xml or XML')
      else:
        raise HandlerException('Provided json does not have a file attribute')

      # start conversion
      xml_string = b64decode(data)
      if self.dump:
        self.dump_file(filename, data)
      
      event = self.stix_converter.convert_stix_xml_string(xml_string, cache_object)
      raise Exception()
      try:
        db_event = self.event_controller.get_event_by_uuid(event.uuid)
        self.logger.debug('Event {0} is in db merging'.format(event.uuid))
        # present in db merge it
        cache_object.reset()
        merger_cache = MergerCache(cache_object)
        self.merger.merge(db_event, event, merger_cache)
        return db_event.to_dict(cache_object)

      except ControllerNothingFoundException:
        self.logger.debug('Event {0} is not in db inserting'.format(event.uuid))
        # not present in db add it
        self.event_controller.insert_event(event, cache_object, True, True)
        return event.to_dict(cache_object)

    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  @rest_method()
  @methods(allowed=['GET'])
  @require()
  def event(self, **args):
    try:
      cache_object = self.get_cache_object(args)
      method = args.get('method', None)
      path = args.get('path')
      requested_object = self.parse_path(path, method)
      event_id = requested_object.get('event_id', None)
      parameters = args.get('parameters')
      if event_id:

        make_file = parameters.get('file', None)
        if make_file == '':
          cherrypy.response.headers['Content-Type'] = 'application/x-download'
          cherrypy.response.headers["Content-Disposition"] = 'attachment; filename=Event_{0}_MISP.xml'.format(event_id)
        else:
          cherrypy.response.headers['Content-Type'] = 'text/xml'

        event = self.event_controller.get_event_by_uuid(event_id)
        self.is_instance_viewable(event, cache_object)
        self.set_event_properties_cache_object(cache_object, event)

        xml_str = self.ce1sus_converter.create_event_xml(event, cache_object)
        return xml_str
      else:
        raise RestHandlerException('Cannot be called witout a valid uuid')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    """
    except ControllerException as error:
      raise RestHandlerException(error)
    """
