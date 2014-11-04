# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 3, 2014
"""
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.base import ControllerException
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminAttributeHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attribute_definition_controller = AttributeDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETEs'])
  @require(privileged())
  def attribute(self, **args):
    try:
      method = args.get('method')
      path = args.get('path')
      headers = args.get('headers')
      details = headers.get('Complete', 'false')
      json = args.get('json')
      if method == 'GET':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          # TODO: add inflate
          definition = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
          if details == 'true':
            return definition.to_dict()
          else:
            return definition.to_dict(complete=False)
        else:
          # else return all
          definitions = self.attribute_definition_controller.get_all_attribute_definitions()
          result = list()
          for definition in definitions:
            if details == 'true':
              result.append(definition.to_dict())
            else:
              result.append(definition.to_dict(complete=False))
          return result
      elif method == 'POST':
        # Add new user
        attr_def = AttributeDefinition()
        attr_def.populate(json)
        # set the new checksum
        self.attribute_definition_controller.insert_attribute_definition(attr_def, self.get_user())
        return attr_def.to_dict()
      elif method == 'PUT':
        # update user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          attr_def = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
          attr_def.populate(json)
          # set the new checksum
          self.attribute_definition_controller.update_attribute_definition(attr_def, self.get_user())
          return attr_def.to_dict()
        else:
          raise RestHandlerException(u'Cannot update user as no identifier was given')

      elif method == 'DELETE':
        # Remove user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          self.attribute_definition_controller.remove_definition_by_id(uuid)
          return 'Deleted Attribute Definition'
        else:
          raise RestHandlerException(u'Cannot delete user as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerException as error:
      raise RestHandlerException(error)
