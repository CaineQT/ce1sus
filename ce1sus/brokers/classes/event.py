from ce1sus.brokers.classes.static import Status, TLP_Level

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

#Created on Jul 5, 2013

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from ce1sus.db.session import Base
from sqlalchemy.types import DateTime
from ce1sus.brokers.classes.permissions import User
from ce1sus.brokers.classes.definitions import DEF_Attribute,DEF_Object

class Ticket(Base):
  __tablename__ = "Tickets"
 
  identifier = Column('ticked_id',Integer, primary_key=True)
  created = Column('created',DateTime)
  ticket = Column('ticket',String)
  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship(User, uselist=False, primaryjoin='User.identifier==Ticket.user_id', innerjoin=True)
  event_id = Column('event_id',ForeignKey('Events.event_id'))

class Attribute(Base):
  __tablename__ = "Attributes"
 
  identifier = Column('attribute_id',Integer, primary_key=True)
  
  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship(User, uselist=False, primaryjoin='User.identifier==Attribute.user_id', innerjoin=True)
  
  def_attribute_id = Column(Integer, ForeignKey('DEF_Attributes.def_attribute_id'))
  definition = relationship(DEF_Attribute,primaryjoin='DEF_Attribute.identifier==Attribute.def_attribute_id', innerjoin=True)
  
  object_id = Column(Integer, ForeignKey('Objects.object_id'))
  object = relationship("Object",primaryjoin='Object.identifier==Attribute.object_id')
  
  __value = None
  
  @property
  def key(self):
    return self.definition.name
  
  @property
  def value(self):
    return self.__value
  
  @value.setter
  def value(self,value):
    self.__value = value
  
  
relationTicketsEvents = Table('Events_has_Tickets', Base.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('ticked_id', Integer, ForeignKey('Tickets.ticked_id'))
)

relationGroupsEvents = Table('Groups_has_Events', Base.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
)

eventsCrossReference = Table('Event_links_Event', Base.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('event_id', Integer, ForeignKey('Events.event_id'))
)

  
class Event(Base):
  __tablename__ = "Events"
 
  identifier = Column('event_id',Integer, primary_key=True)
  
  label = Column('short_description', String)
  description = Column('description',String)
  
  created = Column('created',DateTime)
  first_seen = Column('first_seen',DateTime)
  last_seen = Column('last_seen',DateTime)
  modified = Column('modified',DateTime)
  
  tlp_level_id = Column('tlp_level',Integer)
  published = Column('published',Integer)
  status_id = Column('status',Integer)
  
  comments = relationship("Comment",backref="Events")
  tickets = relationship("Ticket",backref="Events")
  
  user_id = Column(Integer, ForeignKey('Users.user_id'))  
  creator = relationship('User', innerjoin=True)
  
  tickets = relationship("Ticket",secondary=relationTicketsEvents,backref="Tickets")
  
  #groups = relationship("Group")
  
  events = relationship("Event",secondary=eventsCrossReference,backref="Events")
  
  objects = relationship("Object",backref="Events")  
  
  def addObject(self, obj):
    self.objects.append(obj)
    
  @property
  def stauts(self):
    return Status.getByID(self.status_id)
  
  @property
  def tlp(self):
    return TLP_Level.getByID(self.tlp_level_id)
  
class Comment(Base):
  __tablename__ = "Comments"
 
  identifier = Column('comment_id',Integer, primary_key=True)
  #Creator
  user_id = Column(Integer, ForeignKey('Users.user_id'))  
  creator = relationship('User', innerjoin=True)
  #Event witch it belongs to
  event_id = Column(Integer, ForeignKey('Events.event_id'))  
  event = relationship("Event")
  

  
objectsCrossReference = Table('Obj_links_Obj', Base.metadata,
    Column('object_id', Integer, ForeignKey('Objects.object_id')),
    Column('object_id', Integer, ForeignKey('Objects.object_id'))
)

class Object(Base):
  __tablename__ = "Objects"
 
  identifier = Column('object_id',Integer, primary_key=True)
  
  attributes = relationship(Attribute, backref="Objects")
  
  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship("User", uselist=False, primaryjoin='User.identifier==Object.user_id', innerjoin=True)
  
  tlp_level = Column('tlp_level',Integer)
  
  def_object_id = Column(Integer, ForeignKey('DEF_Objects.def_object_id'))  
  definition = relationship(DEF_Object,primaryjoin='DEF_Object.identifier==Object.def_object_id', innerjoin=True)
  
  objects = relationship("Object",secondary=objectsCrossReference,backref="Objects")
  
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False, primaryjoin='Event.identifier==Object.event_id', innerjoin=True)

  def addAttribute(self, attribute):
    self.attributes.append(attribute)
    
class StringValue(Base):
  __tablename__ = "StringValues"
  
  identifier = Column('StringValue_id',Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))  
  attribute = relationship("Attribute",uselist=False, innerjoin=True)
  
  
class DateValue(Base):
  __tablename__ = "DateValues"
  
  identifier = Column('DateValue_id',Integer, primary_key=True)
  value = Column('value', DateTime)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))  
  attribute = relationship("Attribute",uselist=False, innerjoin=True)
  
  
class TextValue(Base):
  __tablename__ = "TextValues"
  
  identifier = Column('TextValue_id',Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))  
  attribute = relationship("Attribute",uselist=False, innerjoin=True)
class NumberValue(Base):
  __tablename__ = "NumberValues"
  identifier = Column('NumberValue_id',Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))  
  attribute = relationship("Attribute",uselist=False, innerjoin=True)