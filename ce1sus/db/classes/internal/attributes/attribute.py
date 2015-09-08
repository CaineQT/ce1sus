# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import FailedValidation, ObjectValidator
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.schema import Table
from sqlalchemy.types import Boolean
from uuid import uuid4

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.attributes.values import ValueBase
from ce1sus.db.classes.internal.core import BaseElement, SimpleLoggingInformations
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_ATTRIBUTE_CONDITIONS = Table('rel_attribute_conditions', getattr(Base, 'metadata'),
                                  Column('condition_id', BigIntegerType, ForeignKey('conditions.condition_id', ondelete='cascade', onupdate='cascade'), primary_key=True, nullable=False, index=True),
                                  Column('attribute_id', BigIntegerType, ForeignKey('attributes.attribute_id', ondelete='cascade', onupdate='cascade'), primary_key=True, nullable=False, index=True)
                                  )

class Condition(SimpleLoggingInformations, Base):
  value = Column('value', UnicodeType(40), unique=True)
  description = Column('description', UnicodeTextType())
  attribute = relationship('Attribute', secondary=_REL_ATTRIBUTE_CONDITIONS, uselist=False)
  _PARENTS = ['attribute']

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'value': self.convert_value(self.value),
            'description': self.convert_value(self.description),
            }

  def validate(self):
    # TODO validate
    return True


class Attribute(BaseElement, Base):
  definition_id = Column('definition_id', BigIntegerType,
                         ForeignKey('attributedefinitions.attributedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship('AttributeDefinition',
                            primaryjoin='AttributeDefinition.identifier==Attribute.definition_id'
                            )
  object_id = Column('object_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  object = relationship('Object', uselist=False)
  # valuerelations
  value_base = relationship(ValueBase,
                            primaryjoin='Attribute.identifier==ValueBase.attribute_id',
                            uselist=False, single_parent=True)

  is_ioc = Column('is_ioc', Boolean)
  # TODO make relation table
  condition_id = Column('condition_id', BigIntegerType, ForeignKey('conditions.condition_id', ondelete='restrict', onupdate='restrict'), index=True, default=None)
  condition = relationship(Condition, uselist=False, secondary=_REL_ATTRIBUTE_CONDITIONS, single_parent=True)

  _PARENTS = ['object']

  @property
  def parent(self):
    return self.object

  def delink_parent(self):
    self.object = None
    self.value_base.event = None
    self.value_base.attribute = None

  def __get_value(self):
    """
    Returns the actual value of an attribute
    """
    value_instance = self.value_base
    # check if the value instance is set
    if value_instance:
      # if the value is not valid
      if isinstance(value_instance, FailedValidation):
        # if the validation has failed return the failed object
        value = value_instance
      else:
        # else return the value of the instance
        value = value_instance.value
      return value
    else:
      return None

  def __set_value(self, new_value):
    if self.definition:
      try:
        value_table = self.definition.value_table
      except AttributeError as error:
        raise error
      classname = '{0}Value'.format(value_table)

      # check if not a value has been assigned
      value_instance = self.value_base
      if value_instance:
        # update only
        value_instance.value = new_value
      else:
        value_instance = get_class('ce1sus.db.classes.internal.attributes.values', classname)
        value_instance = value_instance()
        value_instance.uuid = u'{0}'.format(uuid4())
        value_instance.attribute_id = self.identifier
        value_instance.attribute = self
        value_instance.value = new_value
        value_instance.value_type_id = self.definition.value_type_id

      if self.object:
        event = self.object.event
        if event:
          value_instance.event = event
        else:
          raise ValueError(u'Parent of object was not set.')
      else:
        raise ValueError(u'Cannot set the attribute value as the parent object is not yet set.')

      self.value_base = value_instance

    else:
      raise ValueError(u'Cannot set the attribute value as the definition is not yet set.')

  @property
  def value(self):
    return self.__get_value()

  @property
  def value_instance(self):
    return self.value_base

  @value.setter
  def value(self, value):
    self.__set_value(value)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # validate attribute value
    value_instance = self.value_base
    # TODO: encoding error
    ObjectValidator.validateRegex(value_instance,
                                  'value',
                                  getattr(self.definition, 'regex'),
                                  u'The value "{0}" does not match {1} for definition {2}'.format(value_instance.value,
                                                                                                  getattr(self.definition, 'regex'),
                                                                                                  getattr(self.definition, 'name')).encode('utf-8'),
                                  True)
    if not isinstance(value_instance, FailedValidation):
      errors = not getattr(value_instance, 'validate')()
      if errors:
        return False
    return ObjectValidator.isObjectValid(self)

  def to_dict(self, cache_object):
    instance = self.get_instance(all_attributes=True)
    condition = None
    condition_id = None
    if instance.condition:
      condition = instance.condition.to_dict(cache_object)
      condition_id = instance.convert_value(instance.condition.uuid)

    value = self.convert_value(self.value)
    handler_uuid = '{0}'.format(self.definition.attribute_handler.uuid)
    """
    if handler_uuid in ['0be5e1a0-8dec-11e3-baa8-0800200c9a66', 'e8b47b60-8deb-11e3-baa8-0800200c9a66']:
      # serve file
      fh = self.definition.handler

      filepath = fh.get_base_path() + '/' + value
      # TODO: Find a way not to do this aways
      # with open(filepath, "rb") as raw_file:
      #    value = b64encode(raw_file.read())
    """
    result = {'identifier': instance.convert_value(instance.uuid),
            'definition_id': instance.convert_value(instance.definition.uuid),
            'definition': instance.definition.to_dict(cache_object),
            'ioc': instance.is_ioc,
            'value': value,
            'condition_id': condition_id,
            'condition': condition,
            }
    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
