from sqlalchemy.inspection import inspect
from flask_security import UserMixin, RoleMixin, AsaList
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# !Important: RolesUsers, Role and User are required by flask security. We can add user fields if needed
class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id', ondelete='CASCADE'))
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

    instruments = relationship('Instrument', back_populates='users',cascade="all, delete-orphan")
    band_roles = relationship('BandRole',back_populates='user',cascade="all, delete-orphan")
    events = relationship('Event',secondary='event_user_link',back_populates='users')
    picked_events = relationship('Event',secondary='event_user_picked_link',back_populates='picked_users')
    auditions = relationship('Audition', back_populates='user')

#* Define the models for Audition and Signup
class Audition(Base):
    __tablename__ = 'audition'
    id = Column(Integer, primary_key=True,autoincrement=True)
    details = Column(String(100), nullable=False)
    datetime = Column(DateTime())
    location = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='auditions')
    instrument = Column(String(50))

#* A table for all the events.
class Event(Base):
    __tablename__ = 'event'
    event_id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(200))
    description = Column(String(1000))
    datetime = Column(DateTime())
    location = Column(String(100))

    users = relationship('User',secondary = 'event_user_link',back_populates='events')

    # This is for the users who have been sampled to an event
    picked_users = relationship('User',secondary='event_user_picked_link',back_populates='picked_events')

class EventUserLink(Base):
    __tablename__ = 'event_user_link'
    event_user_link_id =  Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)  # The ID of the user who signed up
    event_id = Column(Integer,ForeignKey('event.event_id'),nullable=False)

class EventUserPickedLink(Base):
    __tablename__ = 'event_user_picked_link'
    event_user_link_id =  Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)  # The ID of the user who signed up
    event_id = Column(Integer,ForeignKey('event.event_id'),nullable=False)

#* The different types of users (following the ERD).
class BandRole(Base):
    __tablename__ = 'band_role'
    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column(Integer(),ForeignKey('user.id', ondelete='CASCADE'))
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

#! This section defines the instruments

class Instrument(Base):
    __tablename__ = 'instrument'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    takes_solos=Column(Boolean, nullable=False, default=False)
    users = relationship('User',back_populates="instruments")
    name = Column(String(50))
    __mapper_args__ = {
        "polymorphic_identity": "instrument",
        "polymorphic_on": "name"
    }
    
    @classmethod
    def get_instrument_attributes(cls):
        instrument_cols = inspect(cls).columns
        parent_cols = inspect(Instrument).columns
        instrument_attributes = [
            attr for attr in instrument_cols if (attr.key not in parent_cols or attr.key == "takes_solos")
        ]
        return instrument_attributes

class Saxophone(Instrument):
    __tablename__ = 'saxophone'
    id = Column(ForeignKey("instrument.id"), primary_key=True)
    alto_1 = Column(Boolean, nullable=False, default=False)
    alto_2 = Column(Boolean, nullable=False, default=False)
    tenor_1 = Column(Boolean, nullable=False, default=False)
    tenor_2 = Column(Boolean, nullable=False, default=False)
    bari = Column(Boolean, nullable=False, default=False)
    sop = Column(Boolean, nullable=False, default=False)
    flute = Column(Boolean, nullable=False, default=False)
    clarinet = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

class Trumpet(Instrument):
    __tablename__ = 'trumpet'
    id = Column(ForeignKey("instrument.id"), primary_key=True)
    trumpet_1 = Column(Boolean, nullable=False, default=False)
    trumpet_2 = Column(Boolean, nullable=False, default=False)
    trumpet_3 = Column(Boolean, nullable=False, default=False)
    trumpet_4 = Column(Boolean, nullable=False, default=False)
    picc_trumpet = Column(Boolean, nullable=False, default=False)
    range_on_trumpet = Column(String(50), nullable=False,default="c2-c4")
    plays_flugal = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

class Trombone(Instrument):
    __tablename__ = 'trombone'
    id = Column(ForeignKey("instrument.id"), primary_key=True)
    trombone_1 = Column(Boolean, nullable=False, default=False)
    trombone_2 = Column(Boolean, nullable=False, default=False)
    trombone_3 = Column(Boolean, nullable=False, default=False)
    range = Column(String(50), nullable=False,default="c2-c4")
    tuba = Column(Boolean, nullable=False, default=False)
    sousaphone = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

class Guitar(Instrument):
    __tablename__ = 'guitar'
    id = Column(ForeignKey("instrument.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

class Piano(Instrument):
    __tablename__ = 'piano'
    id = Column(ForeignKey("instrument.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

class Bass(Instrument):
    __tablename__ = 'bass'
    id = Column(ForeignKey("instrument.id"), primary_key=True)
    double_bass = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

class Drums(Instrument):
    __tablename__ = 'drum'
    id = Column(ForeignKey("instrument.id"), primary_key=True)
    bongos = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

class Percussion(Instrument):
    __tablename__ = 'tuned percussion'
    id = Column(ForeignKey("instrument.id"), primary_key=True)
    bongos = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }