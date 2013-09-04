# -*- coding: utf-8 -*-

"""
module containing all informations about attribute values

Created: Aug 25, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from c17Works.db.broker import BrokerBase, ValidationException, \
NothingFoundException, TooManyResultsFoundException, OperationException, \
BrokerException
import sqlalchemy.orm.exc
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from c17Works.db.session import BASE
from sqlalchemy.types import DateTime
from c17Works.helpers.validator import ObjectValidator
from importlib import import_module

class StringValue(BASE):
  """This is a container class for the STRINGVALUES table."""
  def __init__(self):
    pass

  __tablename__ = "StringValues"

  identifier = Column('StringValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

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



class DateValue(BASE):
  """This is a container class for the DATEVALES table."""
  def __init__(self):
    pass

  __tablename__ = "DateValues"

  identifier = Column('DateValue_id', Integer, primary_key=True)
  value = Column('value', DateTime)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self, 'value')

class TextValue(BASE):
  """This is a container class for the TEXTVALUES table."""
  def __init__(self):
    pass

  __tablename__ = "TextValues"

  identifier = Column('TextValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

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

class NumberValue(BASE):
  """This is a container class for the NUMBERVALUES table."""
  def __init__(self):
    pass

  __tablename__ = "NumberValues"
  identifier = Column('NumberValue_id', Integer, primary_key=True)
  value = Column('value', Integer)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDigits(self, 'value')



class ValueBroker(BrokerBase):
  """
  This broker is used internally to serparate the values to their corresponding tables

  Note: Only used by the AttributeBroker
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.__clazz = StringValue

  @property
  def clazz(self):
    """
    returns the class used for this value broker

    Note: May vary during its lifetime

    """
    return self.__clazz

  @clazz.setter
  def clazz(self, clazz):
    """
    setter for the class
    """
    self.__clazz = clazz

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return self.__clazz

  def __setClassByAttribute(self, attribute):
    """
    sets class for the attribute

    :param attribute: the attribute in context
    :type attribute: Attribute
    """
    className = attribute.definition.className
    module = import_module('.valuebroker', 'ce1sus.brokers')
    self.__clazz = getattr(module, className)

  def __convertAttriuteValueToValue(self, attribute):
    """
    converts an Attribute to a XXXXXValue object

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns: XXXXXValue
    """
    valueInstance = self.__clazz()
    valueInstance.value = attribute.value

    valueInstance.identifier = attribute.value_id
    valueInstance.attribute_id = attribute.identifier
    valueInstance.attribute = attribute
    return valueInstance

  def getByAttribute(self, attribute):
    """
    fetches one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """

    self.__setClassByAttribute(attribute)

    try:
      clazz = self.getBrokerClass()
      result = self.session.query(clazz).filter(
              clazz.attribute_id == attribute.identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No value found with ID :{0} in {1}'.format(
                                  attribute.identifier, self.getBrokerClass()))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
          'Too many value found for ID :{0} in {1}'.format(attribute.identifier,
           self.getBrokerClass()))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result

  def inserByAttribute(self, attribute, commit=True):
    """
    Inserts one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be inserted is invalid')

    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)
    value.identifier = None
    BrokerBase.insert(self, value, commit)

  def updateByAttribute(self, attribute, commit=True):
    """
    updates one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be updated is invalid')

    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)
    BrokerBase.update(self, value, commit)

  def removeByAttribute(self, attribute, commit):
    """
    Removes one XXXXXValue with the information given by the attribtue

    :param attribute: the attribute in context
    :type attribute: Attribute
    :param commit: do a commit after
    :type commit: Boolean
    """
    self.__setClassByAttribute(attribute)

    try:
      self.session.query(self.getBrokerClass()).filter(
                      self.getBrokerClass().attribute_id == attribute.identifier
                      ).delete(synchronize_session='fetch')
      self.doCommit(commit)
    except sqlalchemy.exc.OperationalError as e:
      self.getLogger().error(e)
      self.session.rollback()
      raise OperationException(e)
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def lookforValue(self, clazz, value):
    self.__clazz = clazz
    try:
      return self.session.query(self.getBrokerClass()).filter(
                      self.getBrokerClass().value == value
                      ).all()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

