# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 21, 2015
"""
from sqlalchemy.sql.schema import Table, Column, ForeignKey

from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_MARKINGSTRUCTURE_STATEMENT = Table('rel_markingstructure_statement', getattr(Base, 'metadata'),
                                       Column('rtous_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('markingstructure_id',
                                              BigIntegerType,
                                              ForeignKey('markingstructures.markingstructure_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('statement_id',
                                             BigIntegerType,
                                             ForeignKey('statements.statement_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )


_REL_MARKINGSPECIFICATIONS_INFORMATIONSOURCE = Table('rel_markingspecification_informationsource', getattr(Base, 'metadata'),
                                       Column('rmsis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('markingspecification_id',
                                              BigIntegerType,
                                              ForeignKey('markingspecifications.markingspecification_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('informationsource_id',
                                             BigIntegerType,
                                             ForeignKey('informationsources.informationsource_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )