from database import Base
from flask_security import UserMixin, RoleMixin, AsaList
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey

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

    #! Added outside of flask security.
    request_emails = Column(Boolean(),nullable=False,default=True)
    account_created = Column(DateTime())
    

#* These tables represent the instruments, and which musicians have them.
class MusicianInstrumentLink(Base):
    __tablename__ = 'player_instrument_link'
    id = Column(Integer, primary_key=True,autoincrement=True)
    playerID = Column('playerID',Integer(),ForeignKey('user.id'))
    instrumentID = Column('instrumentID',Integer(),ForeignKey('instrument.instrument_id'))
    
class Instrument(Base):
    __tablename__= 'instrument'
    instrument_id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(255),nullable=False)
    sectionPosition = Column(Integer, nullable=False)
    takesSolos = Column(Boolean())
    highRange = Column(Boolean())


#* Define the models for Audition and Signup
class Audition(Base):
    __tablename__ = 'audition'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(100), nullable=False)
    datetime = Column(DateTime())
    location = Column(String(100))

class AuditionUserLink(Base):
    __tablename__ = 'audition_signup_link'
    signup_link_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # The ID of the user who signed up
    audition_id = Column(Integer, ForeignKey('audition.id'), nullable=False)


#* A table for all the events.
class Event(Base):
    __tablename__ = 'event'
    event_id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(200))
    description = Column(String(100))
    datetime = Column(DateTime())
    location = Column(String(100))

#* The different types of users (following the ERD).
class Musician(Base):
    __tablename__ = 'musician'
    id = Column('id',Integer(),ForeignKey('user.id'),primary_key=True)
    soloing_ability = Column(String(100),nullable=True)

class Singer(Base):
    __tablename__ = 'singer'
    id = Column('id',Integer(),ForeignKey('user.id'),primary_key=True)
    range = Column(String(100),nullable=True)
    audition_video_url = Column(String(200),nullable=True)

class Arranger(Base):
    __tablename__ = 'arranger'
    id = Column('id',Integer(),ForeignKey('user.id'),primary_key=True)
    range = Column(String(100),nullable=True)
    audition_video_url = Column(String(200),nullable=True)