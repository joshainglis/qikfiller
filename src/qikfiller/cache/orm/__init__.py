from os.path import join

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty, backref, scoped_session, sessionmaker

from qikfiller import config_path
from qikfiller.schemas.lists import register_class

Base = declarative_base()

db_path = join(config_path, 'cache.db')

engine = create_engine('sqlite:///{db_path}'.format(db_path=db_path))


class Simple(object):
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self) -> str:
        return '{self.__class__.__name__}(id={self.id}, name={self.name})'.format(self=self)

    def __str__(self) -> str:
        return '{self.name} | {self.id} ({self.__class__.__name__})'.format(self=self)


class HasOwner(object):
    owner_id = Column(Integer)
    owner_name = Column(String)


@register_class
class Category(Base, Simple):
    __tablename__ = 'categories'


@register_class
class Task(Base, Simple, HasOwner):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    custom_fields = Column(String)
    archived = Column(Boolean)
    estimated_hours = Column(Integer)

    client_id = Column(Integer, ForeignKey('clients.id'))
    client = RelationshipProperty('Client')
    parent_id = Column(Integer, ForeignKey('tasks.id'))
    sub_tasks = RelationshipProperty("Task", backref=backref('parent', remote_side=[id]))

    def get_client(self):
        return self.client if self.client_id is not None else self.parent.get_client()


@register_class
class Client(Base, Simple, HasOwner):
    __tablename__ = 'clients'

    custom_fields = Column(String)
    tasks = RelationshipProperty('Task')


@register_class
class TagType(Base, Simple):
    __tablename__ = 'tag_types'

    description = Column(String)


@register_class
class Type(Base, Simple):
    __tablename__ = 'types'

    colour = Column(String)
    enabled = Column(Boolean)
    user_creatable = Column(Boolean)


@register_class
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


Session = scoped_session(sessionmaker())
Session.configure(bind=engine)
