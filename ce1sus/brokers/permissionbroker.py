# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, \
ValidationException, TooManyResultsFoundException
import sqlalchemy.orm.exc
import dagr.helpers.hash as hasher
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from dagr.db.session import BASE
from dagr.db.broker import BrokerException
from dagr.helpers.validator import ObjectValidator
import re

# Relation table for user and groups, ass net agebonnen mai ouni geet et net!?
__REL_USER_GROUPS = Table(
    'User_has_Groups', BASE.metadata,
    Column('user_id', Integer, ForeignKey('Users.user_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
    )

class User(BASE):
  """This is a container class for the USERS table."""
  def __init__(self):
    pass

  __tablename__ = 'Users'
  identifier = Column('user_id', Integer, primary_key=True)
  username = Column('username', String)
  password = Column('password', String)
  privileged = Column('privileged', Integer)
  last_login = Column('last_login', DateTime)
  email = Column('email', String)
  groups = relationship('Group', secondary='User_has_Groups',
                        back_populates='users', cascade='all')
  disabled = Column('disabled', Integer)

  def addGroup(self, group):
    """
    Add a group to this user

    :param group: Group to be added
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be added is invalid')
    function = getattr(self.groups, 'append')
    function(group)

  def removeGroup(self, group):
    """
    Remove a group to this user

    :param group: Group to be removes
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be removed is invalid')
    function = getattr(self.groups, 'remove')
    function(group)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'username', minLength=3)
    # Don't update if the password is already a hash
    if not (self.password == 'EXTERNALAUTH' and re.match('^[0-9a-f]{40}$', self.password) is None):
        ObjectValidator.validateRegex(self,
                                    'password',
                                    ("(?=^.{8,}$)(?=.*[a-z])(?=.*[A-Z])"
                                     + "(?=.*[0-9])(?=.*[\W_])(?=^.*[^\s].*$).*$"),
                                    ('Password has to be set and contain Upper/'
                                     + 'Lower cases, symbols and numbers and have'
                                     + ' at least a length of 8'))
    ObjectValidator.validateDigits(self, 'privileged', minimal=0, maximal=1)
    ObjectValidator.validateEmailAddress(self, 'email')
    if not self.last_login is None:
      ObjectValidator.validateDateTime(self, 'last_login')
    return ObjectValidator.isObjectValid(self)

class Group(BASE):
  """This is a container class for the GRUOPS table."""
  def __init__(self):
    pass

  __tablename__ = 'Groups'
  identifier = Column('group_id', Integer, primary_key=True)
  name = Column('name', String)
  shareTLP = Column('auto_share_tlp', Integer)
  description = Column('description', String)
  users = relationship(User, secondary='User_has_Groups',
                       back_populates='groups', cascade='all')

  def __str__(self):
    return unicode(self.__dict__)

  def addUser(self, user):
    """
    Add a user to this group

    :param user: User to be added
    :type user: User
    """
    errors = not user.validate()
    if errors:
      raise ValidationException('User to be added is invalid')
    function = getattr(self.users, 'append')
    function(user)

  def removeUser(self, user):
    """
    Remove a user to this group

    :param user: User to be removes
    :type user: User
    """
    errors = not user.validate()
    if errors:
      raise ValidationException('User to be removed is invalid')
    function = getattr(self.users, 'remove')
    function(user)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'name',
                                  withSymbols=True)
    ObjectValidator.validateDigits(self, 'shareTLP')
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)

class GroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Group

  def getUsersByGroup(self, identifier, belongIn=True):
    """
    get all users in a given group

    :param identifier: identifier of the group
    :type identifier: Integer
    :param belongIn: If set returns all the attributes of the object else
                     all the attributes not belonging to the object
    :type belongIn: Boolean

    :returns: list of Users
    """
    try:
      users = self.session.query(User).join(Group.users).filter(
                                        Group.identifier == identifier).all()
      if not belongIn:
        userIDs = list()
        for user in users:
          userIDs.append(user.identifier)
        users = self.session.query(User).filter(~User.identifier.in_(
                                                                    userIDs))
      return users
    except sqlalchemy.orm.exc.NoResultFound:
      users = list()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)


  def addGroupToUser(self, userID, groupID, commit=True):
    """
    Add a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
      group.addUser(user)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeGroupFromUser(self, userID, groupID, commit=True):
    """
    Removes a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
      group.removeUser(user)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

class UserBroker(BrokerBase):
  """This is the interface between python an the database"""

  def insert(self, instance, commit=True):
    """
    overrides BrokerBase.insert
    """


    errors = not instance.validate()
    if errors:
      raise ValidationException('User to be inserted is invalid')

    instance.password = hasher.hashSHA1(instance.password,
                                             instance.username)
    try:
      BrokerBase.insert(self, instance, commit)
      self.doCommit(commit)
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def update(self, instance, commit=True):
    """
    overrides BrokerBase.insert
    """



    errors = not instance.validate()
    if errors:
      raise ValidationException('User to be inserted is invalid')

    # Don't update if the password is already a hash
    if re.match('^[0-9a-f]{40}$', instance.password) is None:
      instance.password = hasher.hashSHA1(instance.password,
                                             instance.username)
    try:
      BrokerBase.update(self, instance, commit)
      self.doCommit(commit)
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def isUserPrivileged(self, username):
    """
    Checks if the user has the privileged flag set

    :returns: Boolean
    """
    user = self.getUserByUserName(username)
    if (user.privileged == 1):
      return True
    else:
      return False

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return User

  def getUserByUserName(self, username):
    """
    Returns the user with the following username

    :param user: The username
    :type user: Stirng

    :returns: User
    """
    try:
      user = self.session.query(User).filter(User.username == username).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(username))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for' +
                                         'ID :{0}'.format(username))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return user

  def getUserByUsernameAndPassword(self, username, password):
    """
    Returns the user with the following username and password

    Note: Password will be hashed inside this function

    :param user: The username
    :type user: Stirng
    :param password: The username
    :type password: Stirng

    :returns: User
    """
    passwd = hasher.hashSHA1(password, username)
    try:
      user = self.session.query(User).filter(User.username == username,
                                             User.password == passwd).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(username))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID ' +
                                         ':{0}'.format(username))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return user

  def getGroupsByUser(self, identifier, belongIn=True):
    """
    Returns the groups of the given user

    Note: Password will be hashed inside this function

    :param identifier: identifier of the user
    :type identifier: Integer
    :param belongIn: If set returns all the groups of the user else
                     all the groups not belonging to the user
    :type belongIn: Boolean

    :returns: list of Users

    :returns: User
    """
    try:
      groups = self.session.query(Group).join(User.groups).filter(
                                          User.identifier == identifier).all()
      if not belongIn:
        groupIDs = list()
        for group in groups:
          groupIDs.append(group.identifier)
        groups = self.session.query(Group).filter(~Group.identifier.in_(
                                                                    groupIDs))
    except sqlalchemy.orm.exc.NoResultFound:
      groups = list()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return groups

  def addUserToGroup(self, userID, groupID, commit=True):
    """
    Add a group to a user

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
      user.addGroup(group)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeUserFromGroup(self, userID, groupID, commit=True):
    """
    removes a group to a user

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
      user.removeGroup(group)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
