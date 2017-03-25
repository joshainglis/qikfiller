from os import mkdir
from os.path import abspath, exists, expanduser, join

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty, backref

Base = declarative_base()

qf_path = join(abspath(expanduser('~')), '.qikfiller')
if not exists(qf_path):
    mkdir(qf_path)

db_path = join(qf_path, 'cache.db')

engine = create_engine(f'sqlite:///{db_path}')


class Simple(object):
    id = Column(Integer, primary_key=True)
    name = Column(String)


class HasOwner(object):
    owner_id = Column(Integer)
    owner_name = Column(String)


class Category(Base, Simple):
    __tablename__ = 'categories'


class Task(Base, Simple, HasOwner):
    __tablename__ = 'tasks'

    custom_fields = Column(String)
    archived = Column(Boolean)
    estimated_hours = Column(Integer)

    client_id = Column(Integer, ForeignKey('clients.id'))
    client = RelationshipProperty('Client')
    parent_id = Column(Integer, ForeignKey('tasks.id'))
    sub_tasks = RelationshipProperty("Task", backref=backref('parent', remote_side=[id]))


class Client(Base, Simple, HasOwner):
    __tablename__ = 'clients'

    custom_fields = Column(String)
    tasks = RelationshipProperty('Task')


class TagType(Base, Simple):
    __tablename__ = 'tag_types'

    description = Column(String)


class Type(Base, Simple):
    __tablename__ = 'types'

    colour = Column(String)
    enabled = Column(Boolean)
    user_creatable = Column(Boolean)


class User(Base, Simple):
    __tablename__ = 'users'

    login = Column(String)
    time_zone = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    enabled = Column(Boolean)
    is_admin = Column(Boolean)
    updated_at = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime)
