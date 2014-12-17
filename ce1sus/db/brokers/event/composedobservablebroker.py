# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_, and_, not_, distinct

from ce1sus.db.classes.event import Event
from ce1sus.db.classes.observables import Observable, ObservableComposition
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, \
  TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class ComposedObservableBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return ObservableComposition

  def get_observable_by_id_and_parent_id(self, identifier, parent_id):
    try:
      # Returns an observable belonging to
      result = self.session.query(Observable).join(ObservableComposition.observables).filter(and_(Observable.identifier == identifier, ObservableComposition.parent_id == parent_id)).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No observable found with ID :{0} in composed observable with ID {1}'.format(identifier, parent_id))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for observable with ID {0} in composed observable with ID {1}'.format(identifier, parent_id))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result