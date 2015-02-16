# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug 26, 2013
"""
import random
from sqlalchemy.exc import IntegrityError

from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException, \
  ControllerIntegrityException
from ce1sus.db.common.broker import IntegrityException, BrokerException, ValidationException, DeletionException, NothingFoundException
from ce1sus.helpers.common.datumzait import DatumZait
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class UserController(BaseController):
  """Controller handling all the requests for users"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)

  def get_all_users(self):
    try:
      return self.user_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_user_by_id(self, user_id):
    try:
      return self.user_broker.get_by_id(user_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_user_by_uuid(self, uuid):
    try:
      return self.user_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_user(self, user, validate=True, commit=True):
    try:
      # Add unset elements
      user.activation_str = hashSHA1('{0}{1}'.format(user.plain_password, random.random()))
      user.activation_sent = DatumZait.utcnow()
      if user.plain_password:
        user.password = hashSHA1(user.plain_password)

      # TODO: add api key and mail sending

      self.user_broker.insert(user, validate=validate, commit=commit)

      # if user.gpg_key:
      #  self.mail_handler.import_gpg_key(user.gpg_key)

      # send_mail = self._get_config().get('ce1sus', 'sendmail', False)
      try:
        # if send_mail:
          # send activation mail
        #  self.mail_handler.send_activation_mail(user)
          # activate the user directly
        # else:
        #  user.activated = DatumZait.utcnow()
        #  user.activation_str = None
        #  self.user_broker.update(user)
        # return user, True
        pass
      except Exception as error:
        self.user_broker.update(user)
        self._get_logger().info(u'Could not send activation email to "{0}" for user "{1}" Error:{2}'.format(user.email, user.username, error))
        raise ControllerException(u'Could not send activation email to "{0}" for user "{1}"'.format(user.email, user.username))
    except IntegrityException as error:
      raise ControllerIntegrityException(error)
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(user)
      raise ControllerException(u'Could not add user due to: {0}'.format(message))
    except (BrokerException) as error:
      raise ControllerException(error)

  def update_user(self, user):
    try:
      self.user_broker.update(user)
      # add it again in case of changes
      # TODO import gpg key
      # if user.gpg_key:
      #  self.mail_handler.import_gpg_key(user.gpg_key)
      return user
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(user)
      raise ControllerException(u'Could not update user due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_user_by_id(self, identifier):
    try:
      self.user_broker.remove_by_id(identifier)
    except IntegrityException as error:
      raise ControllerException('Cannot delete user. The user is referenced by elements. Disable this user instead.')
    except DeletionException:
      raise ControllerException('This user cannot be deleted')
    except BrokerException as error:
      raise ControllerException(error)

  def remove_user_by_uuid(self, uuid):
    try:
      self.user_broker.remove_by_uuid(uuid)
    except IntegrityException as error:
      raise ControllerException('Cannot delete user. The user is referenced by elements. Disable this user instead.')
    except DeletionException:
      raise ControllerException('This user cannot be deleted')
    except BrokerException as error:
      raise ControllerException(error)

  def get_user_by_username(self, username):
    try:
      return self.user_broker.getUserByUserName(username)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  """
  def resend_mail(self, user):
    try:
      self.mail_handler.send_activation_mail(user)
      self.user_broker.update(user)
    except Exception as error:
        self.user_broker.update(user)
        self._get_logger().info(u'Could not send activation email to "{0}" for user "{1}" Error:{2}'.format(user.email, user.username, error))
        self.raise_exception(u'Could not send activation email to "{0}" for user "{1}"'.format(user.email, user.username))
    except (BrokerException, MailHandlerException) as error:
      raise ControllerException(error)
      """
