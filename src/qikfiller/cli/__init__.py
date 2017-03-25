from datetime import datetime

import fire
import requests
from six.moves.urllib_parse import urljoin
from sqlalchemy.orm import joinedload

from qikfiller.cache.orm import Base, Category, Client, Session, TagType, Task, Type, User, engine
from qikfiller.schemas.lists.categories import CategoriesSchema
from qikfiller.schemas.lists.client import ClientsSchema
from qikfiller.schemas.lists.tag_types import TagTypesSchema
from qikfiller.schemas.lists.types import TypesSchema
from qikfiller.schemas.lists.user import UsersSchema
from qikfiller.utils.date_time import get_start_end
from qikfiller.utils.fields import get_field, get_task_field
from qikfiller.utils.validation import validate_api_key, validate_url


class QikFiller(object):
    def __init__(self, apikey=None, qik_url=None):
        self.apikey = validate_api_key(apikey)
        self.qik_url = validate_url(qik_url)
        self._session = Session()

    def _get_data(self, type_):
        response = requests.get(urljoin(self.qik_url, '{}.json'.format(type_)), params={'api_key': self.apikey}).json()
        return response

    def init(self):
        Base.metadata.create_all(engine)
        return self

    def load(self):
        users = UsersSchema(strict=True).load(self._get_data('users')).data.users
        for user in users:
            self._session.merge(user)

        tag_types = TagTypesSchema(strict=True).load(self._get_data('tag_types')).data.tagtypes
        for tag_type in tag_types:
            self._session.merge(tag_type)

        types = TypesSchema(strict=True).load(self._get_data('types')).data.types
        for type_ in types:
            self._session.merge(type_)

        categories = CategoriesSchema(strict=True).load(self._get_data('categories')).data.categories
        for category in categories:
            self._session.merge(category)

        clients = ClientsSchema(strict=True).load(self._get_data('tasks')).data.clients
        for client in clients:
            self._session.merge(client)

        self._session.commit()
        return self

    def get_all(self, table):
        return self._session.query(table).all()

    def clients(self, name=None, id=None):
        clients = self._session.query(Client) \
            .options(joinedload('tasks', innerjoin=True).subqueryload('sub_tasks'))
        if name is not None:
            clients = clients.filter(Client.name.ilike('%{name}%'.format(name=name)))
        if id is not None:
            clients = clients.filter(Client.id == id)
        for client in clients.all():
            print(client)
            for task in client.tasks:
                print('  {task}'.format(task=task))
                for sub_task in task.sub_tasks:
                    print('    {sub_task}'.format(sub_task=sub_task))

    def tasks(self, name=None, id=None):
        """
        
        :param name: (optional) Any part of the task name (case insensitive)
        :type name: str
        :param id: (optional) The task id
        :type id: int
        """
        tasks = self._session.query(Task) \
            .options(joinedload('client')) \
            .options(joinedload('parent'))
        if name is not None:
            tasks = tasks.filter(Task.name.ilike('%{name}%'.format(name=name)))
        if id is not None:
            tasks = tasks.filter(Task.id == id)

        for task in tasks.all():
            path = [task]
            t = task
            while t.client is None:
                path.insert(0, t.parent)
                t = t.parent
            path.insert(0, t.client)
            indent = ''
            for p in path:
                print('{indent}{p}'.format(indent=indent, p=p))
                indent += '  '

    def users(self):
        return self.get_all(User)

    def categories(self):
        return self.get_all(Category)

    def tag_types(self):
        return self.get_all(TagType)

    def types(self):
        return self.get_all(Type)

    def create(self, type, task, category, start=None, end=None, duration=None, date=0, description="",
               jira_id="", user='apiuser', dry=False):
        date, start, end = get_start_end(date, start, end, duration)
        type = get_field(self._session, Type, type)
        task = get_task_field(self._session, task)
        category = get_field(self._session, Category, category)

        data = {
            'api_key': self.apikey,
            'entry[start_time]': datetime.combine(date, start).strftime("%Y-%m-%d %H:%M"),
            'entry[end_time]': datetime.combine(date, end).strftime("%Y-%m-%d %H:%M"),
            'entry[type_id]': type,
            'entry[task_id]': task,
            'entry[category_id]': category,
            'entry[owner_id]': user,
            'entry[description]': description,
            'entry[jira_id]': jira_id,
        }

        if dry:
            return data
        else:
            response = requests.post(urljoin(self.qik_url, 'entries.json'), params=data)
            print(response.url)
            print(response.status_code)
            print(response.content)


def main():
    fire.Fire(QikFiller)
