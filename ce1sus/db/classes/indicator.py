# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2014
"""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Unicode, UnicodeText, Integer, BigInteger, DateTime

from ce1sus.common.checks import is_object_viewable
from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties, Marking, TLP
from ce1sus.db.common.session import Base
from stix.common.vocabs import IndicatorType as StixIndicatorType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_INDICATOR_SIGHTINGS = Table('rel_indicator_sightings', Base.metadata,
                                 Column('ris_id', BigInteger, primary_key=True, nullable=False, index=True),
                                 Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                 Column('sighting_id', BigInteger, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                 )


_REL_INDICATOR_KILLCHAINPHASE = Table('rel_indicator_killchainphase', Base.metadata,
                                      Column('rik_id', BigInteger, primary_key=True, nullable=False, index=True),
                                      Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                      Column('killchainphase_id', BigInteger, ForeignKey('killchainphases.killchainphase_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                      )

_REL_INDICATOR_OBSERVABLE = Table('rel_indicator_observable', Base.metadata,
                                  Column('rio_id', BigInteger, primary_key=True, nullable=False, index=True),
                                  Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                  Column('observable_id', BigInteger, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                  )

_REL_INDICATOR_HANDLING = Table('rel_indicator_handling', Base.metadata,
                                Column('rih_id', BigInteger, primary_key=True, nullable=False, index=True),
                                Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                Column('marking_id', BigInteger, ForeignKey('markings.marking_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                )

_REL_KILLCHAIN_KILLCHAINPHASES = Table('rel_killchain_killchainphase', Base.metadata,
                                       Column('rkk_id', BigInteger, primary_key=True, nullable=False, index=True),
                                       Column('killchain_id', BigInteger, ForeignKey('killchains.killchain_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                       Column('killchainphase_id', BigInteger, ForeignKey('killchainphases.killchainphase_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                       )


class Killchain(ExtendedLogingInformations, Base):
  name = Column('name', Unicode(255, collation='utf8_unicode_ci'))
  reference = Column('reference', Unicode(255, collation='utf8_unicode_ci'))
  kill_chain_phases = relationship('KillChainPhase', secondary='rel_killchain_killchainphase')


class KillChainPhase(Base):
  phase_ref = Column('phase_ref', Integer)
  name = Column('name', Unicode(255, collation='utf8_unicode_ci'))
  ordinality = Column('ordinality', Integer)
  phase_id = Column('phase_id', Integer)


class Sighting(ExtendedLogingInformations, Base):
  timestamp_precision = Column('timestamp_precision', Unicode(10, collation='utf8_unicode_ci'))
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  confidence = Column('confidence', Unicode(10, collation='utf8_unicode_ci'), default=u'HIGH', nullable=False)
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code


class IndicatorType(Base):

  type = Column('type', Integer, default=None)
  indicator_id = Column(BigInteger, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {0: StixIndicatorType.TERM_MALICIOUS_EMAIL,
            1: StixIndicatorType.TERM_IP_WATCHLIST,
            2: StixIndicatorType.TERM_FILE_HASH_WATCHLIST,
            3: StixIndicatorType.TERM_DOMAIN_WATCHLIST,
            4: StixIndicatorType.TERM_URL_WATCHLIST,
            5: StixIndicatorType.TERM_MALWARE_ARTIFACTS,
            6: StixIndicatorType.TERM_C2,
            7: StixIndicatorType.TERM_ANONYMIZATION,
            8: StixIndicatorType.TERM_EXFILTRATION,
            9: StixIndicatorType.TERM_HOST_CHARACTERISTICS,
            10: StixIndicatorType.TERM_COMPROMISED_PKI_CERTIFICATE,
            11: StixIndicatorType.TERM_LOGIN_NAME,
            12: StixIndicatorType.TERM_IMEI_WATCHLIST,
            13: StixIndicatorType.TERM_IMSI_WATCHLIST}

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class ValidTimePosition(ExtendedLogingInformations, Base):
  start_time = Column('start_time', DateTime, nullable=False)
  end_time = Column('end_time', DateTime, nullable=False)
  indicator_id = Column('indicator_id', BigInteger, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code


class Indicator(ExtendedLogingInformations, Base):

  version = Column('version', Unicode(40, collation='utf8_unicode_ci'), default=u'1.0.0', nullable=False)
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))
  confidence = Column('confidence', Unicode(5, collation='utf8_unicode_ci'), default=u'HIGH', nullable=False)
  # TODO relation tables
  # TODO Markings
  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  sightings = relationship('Sighting', secondary='rel_indicator_sightings')
  killchains = relationship('KillChainPhase', secondary='rel_indicator_killchainphase')
  types = relationship('IndicatorType')
  handling = relationship(Marking, secondary='rel_indicator_handling')
  operator = Column('operator', Unicode(3, collation='utf8_unicode_ci'))
  observables = relationship('Observable', secondary='rel_indicator_observable')  # 1:*
  valid_time_positions = relationship('ValidTimePosition')  # 1:*
  # TODO add related indicators and TTP
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None

  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """

    return TLP.get_by_id(self.tlp_level_id)

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    self.tlp_level_id = TLP.get_by_value(text)

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code

  def get_observables_for_permissions(self, event_permissions, user):
    rel_objs = list()
    # TODO take into account owner
    for rel_obj in self.observables:
      if is_object_viewable(rel_obj, event_permissions, user):
        rel_objs.append(rel_obj)
    return rel_objs

  def populate(self, json, rest_insert=True):
    self.title = json.get('title', None)
    self.description = json.get('description', None)
    self.short_description = json.get('short_description', None)
    self.operator = json.get('operator', None)
    self.confidence = json.get('confidence', None)
    self.version = json.get('version', None)
    self.properties.populate(json.get('properties', None))
    # TODO: make valid for inflated
    self.properties.is_rest_instert = rest_insert
    self.properties.is_web_insert = not rest_insert
    self.tlp = json.get('tlp', 'Amber').title()

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    if inflated:
      observables = list()
      for observable in self.get_observables_for_permissions(event_permissions, user):
        observables.append(observable.to_dict(complete, inflated, event_permissions, user))

      observables_count = len(observables)
    else:
      observables = None
      # observables_count = self.observables_count_for_permissions(event_permissions)
      observables_count = -1

    if complete:
      result = {'identifier': self.convert_value(self.uuid),
                'description': self.convert_value(self.description),
                'short_description': self.convert_value(self.short_description),
                'confidence': self.convert_value(self.confidence),
                'title': self.convert_value(self.title),
                'properties': self.properties.to_dict(),
                'creator_group': self.creator_group.to_dict(complete, False),
                'modifier_group': self.modifier.group.to_dict(complete, False),
                'originating_group': self.originating_group.to_dict(complete, False),
                'created_at': self.convert_value(self.created_at),
                'modified_on': self.convert_value(self.modified_on),
                'event_id': self.convert_value(self.event.uuid),
                'operator': self.convert_value(self.operator),
                'observables': observables,
                'observables_count': observables_count,
                'version': self.convert_value(self.version),
                'tlp': self.convert_value(self.tlp),
                }
    else:
      result = {'identifier': self.convert_value(self.uuid),
                'short_description': self.convert_value(self.short_description),
                'operator': self.convert_value(self.operator),
                'title': self.convert_value(self.title),
                'properties': self.properties.to_dict(),
                'creator_group': self.creator_group.to_dict(complete, False),
                'modifier_group': self.modifier.group.to_dict(complete, False),
                'originating_group': self.originating_group.to_dict(complete, False),
                'created_at': self.convert_value(self.created_at),
                'modified_on': self.convert_value(self.modified_on),
                'event_id': self.convert_value(self.event.uuid),
                'observables': observables,
                'observables_count': observables_count,
                'version': self.convert_value(self.version),
                'tlp': self.convert_value(self.tlp)
                }

    return result
