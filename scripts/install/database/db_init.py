# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""



import json
import os
import sys

basePath = os.path.dirname(os.path.abspath(__file__)) + '/../../../'
sys.path.insert(0, '../../../')

from ce1sus.helpers.common.config import Configuration
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.admin.mails import MailController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.admin.user import UserController
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.classes.attribute import Condition
from ce1sus.db.classes.definitions import AttributeDefinition, ObjectDefinition
from ce1sus.db.classes.report import ReferenceDefinition
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.handlers.base import HandlerException
from db_data import get_mail_templates, get_users, get_attribute_type_definitions
from maintenance import Maintenance





__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def register_handler(maintenance, registered_list, module_name, type_, class_name):
  try:
    uuid = maintenance.register_handler(module_name, type_, class_name)
    if registered_list.get(type_, None) is None:
      registered_list[type_] = list()

    registered_list[type_].append(uuid)
  except HandlerException:
    pass

if __name__ == '__main__':

    # want parent of parent directory aka ../../
    # setup cherrypy
    #
  ce1susConfigFile = basePath + 'config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  print "Getting config"
  config.get_section('Logger')['log'] = False
  print "Creating DB"
  session = SessionManager(config)
  engine = session.connector.get_engine()
  Base.metadata.create_all(engine, checkfirst=True)
  print "Populating DB and checking/creating gpg db"
  mysql_session = session.connector.get_direct_session()
  session = mysql_session
  user_ctrl = UserController(config, session)
  handler_broker = AttributeHandlerBroker(session)
  print "Populate users"
  all_users = get_users(config)
  users = list()
  for user in all_users:
    user_ctrl.insert_user(user, False, False, False)
    user_ctrl.update_user(user)
    users.append(user)
  user_ctrl.user_broker.do_commit(False)

  # Add handlers
  maintenance = Maintenance(config)

  # Register handlers
  print "Registering handlers"

  registered_handlers = dict()

  register_handler(maintenance, registered_handlers, 'multiplegenerichandler', 'attributes', 'MultipleGenericHandler')
  register_handler(maintenance, registered_handlers, 'filehandler', 'attributes', 'FileHandler')
  register_handler(maintenance, registered_handlers, 'datehandler', 'attributes', 'DateHandler')
  register_handler(maintenance, registered_handlers, 'cbvaluehandler', 'attributes', 'CBValueHandler')
  register_handler(maintenance, registered_handlers, 'texthandler', 'attributes', 'TextHandler')
  register_handler(maintenance, registered_handlers, 'emailhandler', 'attributes', 'EmailHandler')
  register_handler(maintenance, registered_handlers, 'generichandler', 'attributes', 'GenericHandler')
  register_handler(maintenance, registered_handlers, 'filehandler', 'attributes', 'FileWithHashesHandler')

  register_handler(maintenance, registered_handlers, 'filehandler', 'references', 'FileReferenceHandler')
  register_handler(maintenance, registered_handlers, 'generichandler', 'references', 'GenericHandler')
  register_handler(maintenance, registered_handlers, 'linkhandler', 'references', 'LinkHandler')
  register_handler(maintenance, registered_handlers, 'rthandler', 'references', 'RTHandler')
  register_handler(maintenance, registered_handlers, 'texthandler', 'references', 'TextHandler')

  mail_templates = get_mail_templates(users[0])
  print "Populating Mail templates"
  mail_ctrl = MailController(config, session)

  for mail_template in mail_templates:
    mail_ctrl.insert_mail(mail_template, users[0], False)
  mail_ctrl.mail_broker.do_commit(False)

  all_attr_types = get_attribute_type_definitions()
  attr_types = dict()
  print "Populating attribute types"
  attr_ctrl = AttributeDefinitionController(config, session)

  for key, value in all_attr_types.iteritems():

    attr_ctrl.insert_attribute_type(value, False)
    attr_types[key] = value

  attr_ctrl.type_broker.do_commit(False)

  conditions = dict()

  cond_ctrl = ConditionController(config, session)

  with open('conditions.json') as data_file:
    all_conditions = json.load(data_file)
  print "Populating conditions"
  for condition_json in all_conditions:
    condition = Condition()
    condition.populate(condition_json)
    condition.uuid = condition_json.get('identifier')
    conditions[condition.uuid] = condition
    cond_ctrl.insert_condition(condition, False)
  cond_ctrl.condition_broker.do_commit(True)


  # add attributes definitions

  with open('attributes.json') as data_file:
    attrs = json.load(data_file)
  print "Populating attribute definitions"
  attr_dict = dict()
  for attr_json in attrs:
    attr_def = AttributeDefinition()
    attr_def.populate(attr_json)
    attr_def.uuid = attr_json.get('identifier')
    attributehandler_uuid = attr_json.get('attributehandler_id', None)
    if attributehandler_uuid in registered_handlers['attributes']:
      attribute_handler = handler_broker.get_by_uuid(attributehandler_uuid)
      attr_def.attributehandler_id = attribute_handler.identifier
      attr_def.attribute_handler = attribute_handler

      value_type_uuid = attr_json.get('type_id', None)
      value_type = attr_types[value_type_uuid]
      attr_def.value_type_id = value_type.identifier

      default_condition_uuid = attr_json.get('default_condition_id', None)

      default_condition = conditions[default_condition_uuid]
      attr_def.default_condition_id = default_condition.identifier

      attr_ctrl.insert_attribute_definition(attr_def, users[0], False)

      attr_dict[attr_def.uuid] = attr_def

  attr_ctrl.attr_def_broker.do_commit(False)

  # add object definitions and make relations
  with open('objects.json') as data_file:
    objs = json.load(data_file)

  obj_ctrl = ObjectDefinitionController(config, session)
  print "Populating object definitions"
  for obj_json in objs:
    obj_def = ObjectDefinition()
    obj_def.populate(obj_json)
    obj_def.uuid = obj_json.get('identifier')
    attrs = obj_json.get('attributes')
    for attr in attrs:
      uuid = attr.get('identifier')
      if attr_dict.get(uuid, None):
        obj_def.attributes.append(attr_dict[uuid])

    obj_ctrl.insert_object_definition(obj_def, users[0], False)

  obj_ctrl.obj_def_broker.do_commit(False)

  ref_ctrl = ReferencesController(config, session)

  with open('references.json') as data_file:
    references = json.load(data_file)
  print "Populating references definitions"
  for ref_json in references:
    ref_def = ReferenceDefinition()
    ref_def.populate(ref_json)
    ref_def.uuid = ref_json.get('identifier')
    referencehandler_uuid = ref_json.get('referencehandler_id', None)
    if referencehandler_uuid in registered_handlers['references']:
      reference_handler = ref_ctrl.reference_broker.get_handler_by_uuid(referencehandler_uuid)
      ref_def.referencehandler_id = reference_handler.identifier
      ref_def.reference_handler = reference_handler

      ref_ctrl.insert_reference_definition(ref_def, users[0], False)

  ref_ctrl.reference_definition_broker.do_commit(True)
