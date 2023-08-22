from flask_security import UserMixin, RoleMixin, AsaList
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# TODO: Check that each event doesn't need it's own table with all the people playing in it

# !Important: RolesUsers, Role and User are required by flask security. We can add user fields if needed
class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(MutableList.as_mutable(AsaList()), nullable=True)

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(64), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    tf_phone_number = Column(String(128), nullable=True)
    tf_primary_method = Column(String(64), nullable=True)
    tf_totp_secret = Column(String(255), nullable=True)

    #! All below here added outside of flask security.
    request_emails = Column(Boolean(),nullable=False,default=True)
    account_created = Column(DateTime())

    # Notifications 
    notify_about_auditions = Column(Boolean(),nullable=False,default=True)
    notify_about_new_gigs = Column(Boolean(),nullable=False,default=True)
    notify_about_drop_outs = Column(Boolean(),nullable=False,default=True)

    instruments = relationship('Instrument',secondary='player_instrument_link',back_populates='players')
    band_roles = relationship('BandRole',back_populates='user')
    events = relationship('Event',secondary='event_user_link',back_populates='users')
    picked_events = relationship('Event',secondary='event_user_picked_link',back_populates='picked_users')
    auditions = relationship('Audition',secondary ='audition_signup_link', back_populates='signups')

#* These tables represent the instruments, and which musicians have them.
class MusicianInstrumentLink(Base):
    __tablename__ = 'player_instrument_link'
    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column('playerID',Integer(),ForeignKey('user.id'))
    instrument_id = Column('instrumentID',Integer(),ForeignKey('instrument.instrument_id'))
    
class Instrument(Base):
    __tablename__= 'instrument'
    instrument_id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(255),nullable=False)
    sectionPosition = Column(Integer, nullable=False)
    takesSolos = Column(Boolean())
    highRange = Column(Boolean())

    players = relationship('User', secondary='player_instrument_link',back_populates='instruments')

#* Define the models for Audition and Signup
class Audition(Base):
    __tablename__ = 'audition'
    id = Column(Integer, primary_key=True,autoincrement=True)
    details = Column(String(100), nullable=False)
    datetime = Column(DateTime())
    location = Column(String(100))
    signups = relationship('User',secondary='audition_signup_link',back_populates='auditions')

class AuditionUserLink(Base):
    __tablename__ = 'audition_signup_link'
    signup_link_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # The ID of the user who signed up
    audition_id = Column(Integer, ForeignKey('audition.id'), nullable=False)
    instrument_id = Column(Integer, ForeignKey('instrument.instrument_id'), nullable=False)


#* A table for all the events.
class Event(Base):
    __tablename__ = 'event'
    event_id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(200))
    description = Column(String(100))
    datetime = Column(DateTime())
    location = Column(String(100))

    users = relationship('User',secondary = 'event_user_link',back_populates='events')

    # This is for the users who have been sampled to an event
    picked_users = relationship('User',secondary='event_user_picked_link',back_populates='picked_events')

class EventUserLink(Base):
    __tablename__ = 'event_user_link'
    event_user_link_id =  Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # The ID of the user who signed up
    event_id = Column(Integer,ForeignKey('event.event_id'),nullable=False)

class EventUserPickedLink(Base):
    __tablename__ = 'event_user_picked_link'
    event_user_link_id =  Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # The ID of the user who signed up
    event_id = Column(Integer,ForeignKey('event.event_id'),nullable=False)

#* The different types of users (following the ERD).
class BandRole(Base):
    __tablename__ = 'band_role'
    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column(Integer(),ForeignKey('user.id'))
    role_type = Column(String(20))

    user = relationship('User',back_populates='band_roles')

    __mapper_args__ = {
        'polymorphic_identity': 'role',
        'polymorphic_on': role_type
    }

class Musician(BandRole):
    __mapper_args__ = {'polymorphic_identity': 'musician'}

class Singer(BandRole):
    __mapper_args__ = {'polymorphic_identity': 'singer'}
    vocal_range = Column(String(100),nullable=True)
    singer_audition_video_url = Column(String(200),nullable=True)

class Arranger(BandRole):
    __mapper_args__ = {'polymorphic_identity': 'arranger'}
    arranger_audition_video_url = Column(String(200),nullable=True)