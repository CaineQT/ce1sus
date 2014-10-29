# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Unicode, Integer, Text, BIGINT

from ce1sus.db.common.session import Base
from ce1sus.helpers.bitdecoder import BitBase
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_MAINGROUP_GROUPS = Table('group_has_groups', Base.metadata,
                              Column('ghg_id', BIGINT, primary_key=True, nullable=False, index=True),
                              Column('group_id', BIGINT, ForeignKey('groups.group_id', onupdate='cascade', ondelete='cascade'), index=True),
                              Column('rel_group_id', BIGINT, ForeignKey('groups.group_id', onupdate='cascade', ondelete='cascade'), index=True))


class GroupRights(BitBase):
  """
  The __bit_value is defined as follows:
  [0] : User is privileged
  [1] : User can validate
  [2] : User can set group via rest inserts
  """

  DOWNLOAD = 0
  TLP_PROPAGATION = 1

  @property
  def can_download(self):
    return self._get_value(GroupRights.DOWNLOAD)

  @can_download.setter
  def can_download(self, value):
    self._set_value(GroupRights.DOWNLOAD, value)

  @property
  def propagate_tlp(self):
    return self._get_value(GroupRights.TLP_PROPAGATION)

  @propagate_tlp.setter
  def propagate_tlp(self, value):
    self._set_value(GroupRights.TLP_PROPAGATION, value)


class EventPermissions(BitBase):

  VIEW = 0
  # Add directly without validation
  ADD = 1
  MODIFY = 2
  DELETE = 3
  VALIDATE = 4
  PROPOSE = 5

  @property
  def can_propose(self):
    return self._get_value(EventPermissions.PROPOSE)

  @can_propose.setter
  def can_propose(self, value):
    # Note if you can propose, you can see
    if not self.can_view:
      self.can_view = True
    self._set_value(EventPermissions.PROPOSE, value)

  @property
  def can_view(self):
    return self._get_value(EventPermissions.VIEW)

  @can_view.setter
  def can_view(self, value):
    # if you can see you can propose
    if not self.can_propose:
      self.can_propose = True
    self._set_value(EventPermissions.VIEW, value)

  @property
  def can_add(self):
    return self._get_value(EventPermissions.ADD)

  @can_add.setter
  def can_add(self, value):
    # if you can add you can see
    if not self.can_view:
      self.can_view = True
    self._set_value(EventPermissions.ADD, value)

  @property
  def can_modify(self):
    return self._get_value(EventPermissions.MODIFY)

  @can_modify.setter
  def can_modify(self, value):
    # if you can modify you can see
    if not self.can_view:
      self.can_view = True
    self._set_value(EventPermissions.MODIFY, value)

  @property
  def can_delete(self):
    return self._get_value(EventPermissions.DELETE)

  @can_delete.setter
  def can_delete(self, value):
    # if you can delete you can see
    if not self.can_view:
      self.can_view = True
    self._set_value(EventPermissions.DELETE, value)

  @property
  def can_validate(self):
    return self._get_value(EventPermissions.VALIDATE)

  @can_validate.setter
  def can_validate(self, value):
    # if you can validate you can see
    if not self.can_view:
      self.can_view = True
    self._set_value(EventPermissions.VALIDATE, value)


class Group(Base):
  name = Column('name', Unicode(255), nullable=False, unique=True)
  description = Column('description', Text)
  tlp_lvl = Column('tlplvl', Integer, default=4, nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None
  __default_bit_code = None
  default_dbcode = Column('default_code', Integer, default=0, nullable=False)
  children = relationship('Group',
                          secondary=_REL_MAINGROUP_GROUPS,
                          primaryjoin='Group.identifier == group_has_groups.c.group_id',
                          secondaryjoin='Group.identifier == group_has_groups.c.rel_group_id',
                          backref='parents',
                          order_by='Group.name',
                          )

  @property
  def default_permissions(self):
    if self.__default_bit_code is None:
      if self.default_dbcode is None:
        self.__default_bit_code = EventPermissions('0', self, 'default_dbcode')
      else:
        self.__bit_code = EventPermissions(self.default_dbcode, self, 'default_dbcode')
    return self.__default_bit_code

  @property
  def permissions(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = GroupRights('0', self)
      else:
        self.__bit_code = GroupRights(self.dbcode, self)
    return self.__bit_code

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Verify validation of Group Object
    ObjectValidator.validateAlNum(self, 'name',
                                  withSymbols=True,
                                  minLength=3)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)
