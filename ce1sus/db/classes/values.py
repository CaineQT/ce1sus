# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 17, 2014
"""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, Numeric, Date, BigInteger, DateTime

from ce1sus.db.common.session import Base
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# TODO: recheck validation of values
class ValueBase(object):

  @declared_attr
  def attribute_id(self):
    return Column('attribute_id', BigInteger, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @declared_attr
  def attribute(self):
    return relationship('Attribute', uselist=False, lazy='joined')

  @declared_attr
  def event_id(self):
    return Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @declared_attr
  def event(self):
    return relationship("Event", uselist=False)

  @declared_attr
  def value_type_id(self):
    return Column('attributetype_id', BigInteger, ForeignKey('attributetypes.attributetype_id'), nullable=False, index=True)

  @declared_attr
  def value_type(self):
    return relationship('AttributeType', uselist=False)


# pylint: disable=R0903,W0232
class StringValue(ValueBase, Base):
  """This is a container class for the STRINGVALUES table."""

  value = Column('value', Unicode(255, collation='utf8_unicode_ci'), nullable=False, index=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self,
                                         'value',
                                         minLength=1,
                                         withSpaces=True,
                                         withSymbols=True)


# pylint: disable=R0903
class DateValue(ValueBase, Base):
  """This is a container class for the DATEVALES table."""
  value = Column('value', Date, nullable=False, index=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return True


# pylint: disable=R0903
class TimeStampValue(ValueBase, Base):
  """This is a container class for the DATEVALES table."""
  value = Column('value', DateTime, nullable=False, index=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDateTime(self, 'value')


# pylint: disable=R0903
class TextValue(ValueBase, Base):
  """This is a container class for the TEXTVALUES table."""
  value = Column('value', UnicodeText(collation='utf8_unicode_ci'), nullable=False)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self,
                                         'value',
                                         minLength=1,
                                         withNonPrintableCharacters=True,
                                         withSpaces=True,
                                         withSymbols=True)


# pylint: disable=R0903
class NumberValue(ValueBase, Base):
  """This is a container class for the NUMBERVALUES table."""
  value = Column('value', Numeric, nullable=False, index=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDigits(self, 'value')
