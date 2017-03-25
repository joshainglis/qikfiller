import sys
from datetime import datetime
from os import getenv
from urllib.parse import urlencode, urljoin

import fire
import requests
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session as SQLASession

from qikfiller.cache.orm import Base, Category, Client, Session, TagType, Task, Type, User, engine
from qikfiller.schemas.lists.categories import CategoriesSchema
from qikfiller.schemas.lists.client import ClientsSchema
from qikfiller.schemas.lists.tag_types import TagTypesSchema
from qikfiller.schemas.lists.types import TypesSchema
from qikfiller.schemas.lists.user import UsersSchema
from qikfiller.utils.date_time import parse_date, parse_time, to_timedelta

QIK_API_KEY = getenv('QIK_API_KEY')
QIK_URL = getenv('QIK_URL')


def get_field(session, table, field):
    if not isinstance(field, int):
        fields = session.query(table).filter(table.name.ilike(f'%{field}%')).all()
        if len(fields) == 0:
            print(f'Could not find any {table.__tablename__} matching "{field}"')
            sys.exit(1)
        elif len(fields) > 1:
            t = [(f'{field_.id}', f'{field_.name}') for field_ in fields]
            l = [max(len(x[y]) for x in t) for y in range(len(t[0]))]
            for type_ in t:
                print('{{0:<{0}s}}: {{1:<{1}s}}'.format(*l).format(*type_))
            field = int(input(f'Please enter the id of desired {table.__class__.__name__.lower()} from above: '))
        else:
            field = fields[0].id
    return field


def get_task_field(session, task_id):
    if not isinstance(task_id, int):
        task_id_split = task_id.split(':')
        if task_id_split[-1]:
            tasks = session.query(Task).filter(Task.name.ilike(f'%{task_id_split[-1]}%')).all()
        else:
            tasks = session.query(Task).all()
        if len(task_id_split) == 2:
            tasks = [task for task in tasks if task_id_split[0].lower() in task.get_client().name.lower()]
        if len(tasks) == 0:
            print(f'Could not find any task matching "{task_id}"')
            sys.exit(1)
        elif len(tasks) > 1:
            t = [(f'{type_.id}', f'{type_.get_client().name}', f'{type_.name}') for type_ in tasks]
            l = [max(len(x[y]) for x in t) for y in range(len(t[0]))]
            for type_ in t:
                print('{{0:<{0}s}}: {{1:<{1}s}}: {{2:<{2}s}}'.format(*l).format(*type_))
            task_id = int(input(f'Please enter the id of desired task from above: '))
        else:
            task_id = tasks[0].id
    return task_id


class QikFiller(object):
    def __init__(self, apikey=None, qik_url=None):
        self.apikey = self._validate_api_key(apikey)
        self.qik_url = self._validate_url(qik_url)
        self._session: SQLASession = Session()

    @staticmethod
    def _validate_api_key(apikey):
        apikey = apikey if apikey is not None else QIK_API_KEY
        if apikey is None:
            print("Please provide your QIK API key")
            sys.exit(1)
        return apikey

    @staticmethod
    def _validate_url(qik_url):
        qik_url = qik_url if qik_url is not None else QIK_URL
        if qik_url is None:
            print("Please provide your the url to you QikTimes instance")
            sys.exit(1)
        return qik_url

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
            clients = clients.filter(Client.name.ilike(f'%{name}%'))
        if id is not None:
            clients = clients.filter(Client.id == id)
        for client in clients.all():
            print(client)
            for task in client.tasks:
                print(f'  {task}')
                for sub_task in task.sub_tasks:
                    print(f'    {sub_task}')

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
            tasks = tasks.filter(Task.name.ilike(f'%{name}%'))
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
                print(f'{indent}{p}')
                indent += '  '
                # print(task)
                # for task in task.tasks:
                #     print(f'  {task}')
                #     for sub_task in task.sub_tasks:
                #         print(f'    {sub_task}')

    def users(self):
        return self.get_all(User)

    def categories(self):
        return self.get_all(Category)

    def tag_types(self):
        return self.get_all(TagType)

    def types(self):
        return self.get_all(Type)

    def create(self, type_id, task_id, category_id, start=None, end=None, duration=None, date=0, description="",
               jira_id="", user='apiuser', dry=False):
        date = parse_date(date)
        if start and end:
            start = parse_time(start)
            end = parse_time(end)
        elif start and duration:
            start = parse_time(start)
            end = (datetime.combine(date, start) + to_timedelta(parse_time(duration))).time()
        elif end and duration:
            end = parse_time(end)
            start = (datetime.combine(date, end) - to_timedelta(parse_time(duration))).time()
        else:
            raise ValueError("Please provide any two of start, end, duration")
        if start > end:
            raise ValueError(f'Start time {start} is after end time {end}.')

        type_id = get_field(self._session, Type, type_id)
        task_id = get_task_field(self._session, task_id)
        category_id = get_field(self._session, Category, category_id)

        data = {
            'api_key': self.apikey,
            'entry[start_time]': datetime.combine(date, start).strftime("%Y-%m-%d %H:%M"),
            'entry[end_time]': datetime.combine(date, end).strftime("%Y-%m-%d %H:%M"),
            'entry[type_id]': type_id,
            'entry[task_id]': task_id,
            'entry[category_id]': category_id,
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
