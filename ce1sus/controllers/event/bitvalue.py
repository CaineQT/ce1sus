# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Nov 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from dagr.db.broker import BrokerException


class BitValueController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)

  @staticmethod
  def __set_shared(instance, share):

    if share == '1':
      instance.bit_value.is_shareable = True
    else:
      instance.bit_value.is_shareable = False

  @staticmethod
  def __set_validated(instance, validated):
    if validated == '1':
      instance.bit_value.is_validated = True
    else:
      instance.bit_value.is_validated = False

  @staticmethod
  def __set_share_object(obj, share, use_default):
    BitValueController.__set_shared(obj, share)

    if (obj.bit_value.is_shareable):
      if use_default == '1':
        for attribute in obj.attributes:
          if attribute.definition.share == 1:
            attribute.bit_value.is_shareable = True
          else:
            attribute.bit_value.is_shareable = False
      else:
        # Dont change the values
        pass
    else:
      # if the value changed change also all share values of its attributes
      for attribute in obj.attributes:
        BitValueController.__set_shared(attribute, share)

  def get_object_by_id(self, object_id):
    try:
      return self.object_broker.get_by_id(object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def set_object_values(self, user, event, obj, share, validated='1', use_default=None):
    try:
      user = self._get_user(user.username)
      self.event_broker.update_event(user, event, False)
      BitValueController.__set_share_object(obj, share, use_default)
      BitValueController.__set_validated(obj, validated)
      self.object_broker.update_object(user, obj, commit=False)
      self.object_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)

  def get_attribute_by_id(self, attr_id):
    try:
      return self.attribute_broker.get_by_id(attr_id)
    except BrokerException as error:
      self._raise_exception(error)

  def set_attribute_values(self, user, event, attribute, share, validated='1'):
    try:
      user = self._get_user(user.username)
      self.event_broker.update_event(user, event, False)

      self.object_broker.update_object(user, attribute.object, commit=False)
      BitValueController.__set_shared(attribute, share)
      BitValueController.__set_validated(attribute, validated)
      self.attribute_broker.update_attribute(user, attribute, False)
      self.attribute_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)