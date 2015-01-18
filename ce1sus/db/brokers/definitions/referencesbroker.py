# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 21, 2014
"""


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from ce1sus.db.classes.report import ReferenceDefinition, ReferenceHandler
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReferencesBroker(BrokerBase):

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    return ReferenceDefinition

  def get_all_handlers(self):
    try:
      result = self.session.query(ReferenceHandler)
      return result.all()
    except SQLAlchemyError as error:
      raise BrokerException(error)


class ReferenceDefintionsBroker(BrokerBase):

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    return ReferenceDefinition

  def get_defintion_by_chksums(self, chksums):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definitions = self.session.query(self.get_broker_class()).filter(getattr(self.get_broker_class(), 'chksum').in_(chksums)).all()
      if definitions:
        return definitions
      else:
        return list()
    except NoResultFound:
      raise NothingFoundException(u'No {0} not found for CHKSUMS {1}'.format(self.get_broker_class().__class__.__name__,
                                                                             chksums))
    except SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)