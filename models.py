from database import Base
from flask_security import UserMixin, RoleMixin, AsaList
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey

# TODO: Check that these models have all the needed fields

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
    
class PlayersInstruments(Base):
    __tablename__ = 'players_instruments'
    id = Column(Integer, primary_key=True,autoincrement=True)
    playerID = Column('playerID',Integer(),ForeignKey('user.id'))
    instrumentID = Column('instrumentID',Integer(),ForeignKey('instruments.instrumentID'))
    

class Instruments(Base):
    __tablename__= 'instruments'
    instrumentID = Column(Integer, primary_key=True,autoincrement=True)
    instrumentName = Column(String(255),nullable=False)
    sectionPosition = Column(Integer, nullable=False)
    takesSolos = Column(Boolean())
    highRange = Column(Boolean())


# Define the models for Audition and Signup
class Audition(Base):
    __tablename__ = 'audition'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(100), nullable=False)
    # Add other audition details as needed

class Signup(Base):
    __tablename__ = 'signups'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # The ID of the user who signed up
    audition_id = Column(Integer, ForeignKey('audition.id'), nullable=False)


class Gigs(Base):
    __tablename__ = 'gigs'
    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(200))
    description = Column(String(100))
    date = Column(DateTime())
    location = Column(String(100))
