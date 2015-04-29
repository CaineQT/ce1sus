# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from ce1sus.controllers.base import BaseController
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.observables import Observable, ObservableComposition
from ce1sus.mappers.stix.helpers.common import extract_uuid, make_dict_definitions, set_extended_logging, set_properties
from cybox.objects.address_object import Address
from cybox.objects.domain_name_object import DomainName
from cybox.objects.file_object import File
from cybox.objects.hostname_object import Hostname
from cybox.objects.uri_object import URI
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CyboxMapperException(Exception):
  pass


class CyboxMapper(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    # cache all definitions
    self.condition_broker = self.broker_factory(ConditionBroker)

  def init(self):
    attr_defs = self.attr_def_broker.get_all()
    self.attr_defs = make_dict_definitions(attr_defs)
    obj_defs = self.obj_def_broker.get_all()
    self.obj_defs = make_dict_definitions(obj_defs)
    conditions = self.condition_broker.get_all()
    self.conditions = self.make_dict_conditions(conditions)

  def make_dict_conditions(self, conditions):
    result = dict()
    for condition in conditions:
      result[condition.value] = condition
    return result

  def get_object_definition(self, instance):
    definition = None
    if isinstance(instance, Hostname):
      definition = self.obj_defs.get('Hostname')
    elif isinstance(instance, Address):
      if instance.category == 'e-mail':
        definition = self.obj_defs.get('email')
      else:
        raise CyboxMapperException(u'Note defined')
    elif isinstance(instance, File):
      definition = self.obj_defs.get('File')
    elif isinstance(instance, URI):
      definition = self.obj_defs.get('URI')
    elif isinstance(instance, DomainName):
      definition = self.obj_defs.get('DomainName')
    if definition:
      return definition
    else:
      raise CyboxMapperException(u'Object mapping for {0} is not defined'.format(instance))

  def get_attribute_definition(self, instance):
    definition = None
    if isinstance(instance, Hostname):
      definition = self.attr_defs.get(u'Hostname_Value')
    elif isinstance(instance, Address):
      if instance.category == 'e-mail':
        if instance.is_source:
          definition = self.attr_defs.get('email_sender')
        elif instance.is_destination:
          definition = self.attr_defs.get('email_to')
        else:
          # it can only be source that makes sense
          definition = self.attr_defs.get('email_sender')
      else:
        raise CyboxMapperException(u'Note defined')
    elif isinstance(instance, URI):
      if instance.type_ == 'URL':
        definition = self.attr_defs.get('url')
      else:
        raise CyboxMapperException(u'Note defined')
    elif isinstance(instance, DomainName):
      definition = self.attr_defs.get('DomainName_Value')
    if definition:
      return definition
    else:
      raise CyboxMapperException(u'Attribute mapping for {0} is not defined'.format(instance))

  def __create_attribute_by_def(self, def_name, parent, value, is_indicator, condition=None, tlp=None):
    attribute = Attribute()
    set_properties(attribute)
    attribute.object = parent
    attribute.is_ioc = is_indicator
    attribute.definition = self.attr_defs.get(def_name, None)
    db_cond = None
    if condition:
      db_cond = self.conditions[condition]

    else:
      db_cond = self.conditions['Equals']
    attribute.condition = db_cond
    attribute.condition_id = db_cond.identifier

    if not attribute.definition:
      raise CyboxMapperException('Definition {0} is not definied'.format(def_name))
    attribute.value = value
    return attribute

  def create_file_attributes(self, cybox_file, parent, is_indicator):
    attributes = list()
    if cybox_file.encryption_algorithm:
      attributes.append(self.__create_attribute_by_def('encryption_mechanism', parent, cybox_file.encryption_algorithm, is_indicator))
    if cybox_file.accessed_time:
      attributes.append(self.__create_attribute_by_def('Accessed_Time', parent, cybox_file.accessed_time, is_indicator))
    if cybox_file.created_time:
      attributes.append(self.__create_attribute_by_def('Created_Time', parent, cybox_file.created_time, is_indicator))
    if cybox_file.file_extension:
      attributes.append(self.__create_attribute_by_def('File_Extension', parent, cybox_file.file_extension, is_indicator))
    if cybox_file.full_path and cybox_file.full_path.condition == 'Equals':
      attributes.append(self.__create_attribute_by_def('Full_Path', parent, cybox_file.full_path, is_indicator))
    if cybox_file.full_path and cybox_file.full_path.condition == 'Like':
      attributes.append(self.__create_attribute_by_def('file_full_path_pattern', parent, cybox_file.full_path, is_indicator))
    if cybox_file.modified_time:
      attributes.append(self.__create_attribute_by_def('file_modified_time', parent, cybox_file.modified_time, is_indicator))
    if cybox_file.file_name and cybox_file.file_name.condition:
      if cybox_file.file_name.condition == 'Equals':
        attributes.append(self.__create_attribute_by_def('File_Name', parent, cybox_file.file_name, is_indicator))
      if cybox_file.file_name.condition == 'Like':
        attributes.append(self.__create_attribute_by_def('file_name_pattern', parent, cybox_file.file_name, is_indicator))
    elif cybox_file.file_name:
      # Default condition is EQUAL
      attributes.append(self.__create_attribute_by_def('File_Name', parent, cybox_file.file_name, is_indicator))
    if cybox_file.hashes:
      # TODO: clean up  when cybox implements this differently
      try:
        if cybox_file.hashes.md5:
          attributes.append(self.__create_attribute_by_def('hash_md5', parent, cybox_file.hashes.md5, is_indicator))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha1:
          attributes.append(self.__create_attribute_by_def('hash_sha1', parent, cybox_file.hashes.sha1, is_indicator))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha256:
          attributes.append(self.__create_attribute_by_def('hash_sha256', parent, cybox_file.hashes.sha256, is_indicator))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha384:
          attributes.append(self.__create_attribute_by_def('hash_sha384', parent, cybox_file.hashes.sha384, is_indicator))
      except AttributeError:
        pass
      try:
        if cybox_file.hashes.sha512:
          attributes.append(self.__create_attribute_by_def('hash_sha512', parent, cybox_file.hashes.sha512, is_indicator))
      except AttributeError:
        pass

    if cybox_file.size:
      attributes.append(self.__create_attribute_by_def('Size_In_Bytes', parent, cybox_file.size, is_indicator))
    if cybox_file.file_extension:
      attributes.append(self.__create_attribute_by_def('File_Extension', parent, cybox_file.file_extension, is_indicator))

    if attributes:
      return attributes
    else:
      raise CyboxMapperException('No attribute was created for file')

  def create_attributes(self, properties, parent_object, tlp_id, is_indicator):
    # TODO: Create custom properties
    attribute = Attribute()
    attribute.tlp_level_id = tlp_id
    attribute.object = parent_object
    attribute.is_ioc = is_indicator
    set_properties(attribute)
    if isinstance(properties, Hostname):
      prop = properties.hostname_value
    elif isinstance(properties, Address):
      prop = properties.address_value
    elif isinstance(properties, File):
      return self.create_file_attributes(properties, parent_object, is_indicator)
    elif isinstance(properties, URI):
      prop = properties.value
    elif isinstance(properties, DomainName):
      prop = properties.value
    else:
      raise CyboxMapperException('No attribute definiton defined for {0}'.format(properties))
    counter = 0
    for value in prop.values:
      # TODO Check if there are more values in hostname
      attribute.definition = self.get_attribute_definition(properties)
      attribute.value = value
      counter = counter + 1
    if counter > 1:
      raise CyboxMapperException(u'More values are present but this is not yet implemented')
    attribute.condition = prop.condition

    if attribute.value:
      return [attribute]
    else:
      raise CyboxMapperException(u'Attribute mapping for {0} is not defined'.format(properties))

  def create_object(self, cybox_object, observable, user, tlp_id, is_indicator):
    ce1sus_object = Object()
    ce1sus_object.tlp_level_id = tlp_id
    set_properties(ce1sus_object)
    # Create the container
    ce1sus_object.observable = observable
    ce1sus_object.uuid = extract_uuid(cybox_object.id_)
    ce1sus_object.definition = self.get_object_definition(cybox_object.properties)
    set_extended_logging(ce1sus_object, user, user.group)

    # Create attributes
    attributes = self.create_attributes(cybox_object.properties, ce1sus_object, tlp_id, is_indicator)
    for attribute in attributes:
      set_extended_logging(attribute, user, user.group)

    ce1sus_object.attributes = attributes

    # TODO: related_objects
    return ce1sus_object

  def create_observable(self, observable, event, user, tlp_id, is_indicator=False):
    ce1sus_observable = Observable()
    ce1sus_observable.tlp_level_id = tlp_id
    set_properties(ce1sus_observable)
    if observable.id_:
      ce1sus_observable.uuid = extract_uuid(observable.id_)

    set_extended_logging(ce1sus_observable, user, user.group)
    ce1sus_observable.event = event
    ce1sus_observable.parent = event
    # an observable has either a composition or a single object
    if observable.observable_composition:
      composition = ObservableComposition()
      composition.operator = observable.observable_composition.operator
      for child in observable.observable_composition.observables:
        child_observable = self.create_observable(child, event, user, tlp_id, is_indicator)
        # As the observable is not on the root level remove the link to the parent
        child_observable.event = None
        composition.observables.append(child_observable)
      ce1sus_observable.observable_composition = composition
    else:

      ce1sus_observable.uuid = extract_uuid(observable.id_)
      # create a cybox object
      obj = self.create_object(observable.object_, ce1sus_observable, user, tlp_id, is_indicator)
      ce1sus_observable.object = obj
      # TODO

    return ce1sus_observable
