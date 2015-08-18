# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 28, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_INFRASTRUCTURE_STRUCTUREDTEXT = Table('rel_infrastructure_structuredtext', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('infrastructure_id',
                                              BigIntegerType,
                                              ForeignKey('infrastructures.infrastructure_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

_REL_INFRASTRUCTURE_STRUCTUREDTEXT_SHORT = Table('rel_infrastructure_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('infrastructure_id',
                                              BigIntegerType,
                                              ForeignKey('infrastructures.infrastructure_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )


class Infrastructure(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{3}'.format(self.namespace, self.__class__.__name__, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['resource']

  title = Column('title', UnicodeType(255), index=True, nullable=True)
  description = relationship(StructuredText, secondary=_REL_INFRASTRUCTURE_STRUCTUREDTEXT, uselist=False, backref='infrastructure_description')
  short_description = relationship(StructuredText, secondary=_REL_INFRASTRUCTURE_STRUCTUREDTEXT_SHORT, uselist=False, backref='infrastructure_short_description')

  # custom ones related to ce1sus internals
  ttpresource_id = Column('ttpresource_id', BigIntegerType, ForeignKey('resources.resource_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  def to_dict(self, cache_object):

    result = {
              'id_': self.convert_value(self.id_),
              'title': self.convert_value(self.title),
              'description': self.attribute_to_dict(self.description, cache_object),
              'short_description': self.attribute_to_dict(self.short_description, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
