from datetime import date, datetime, timedelta

import fire
import requests
from six.moves.urllib_parse import urljoin
from sqlalchemy.orm import joinedload

from qikfiller.cache.orm import Base, Category, Client, Profile, Session, TagType, Task, Type, User, engine
from qikfiller.constants import ALL
from qikfiller.schemas.lists.categories import CategoriesSchema
from qikfiller.schemas.lists.client import ClientsSchema
from qikfiller.schemas.lists.tag_types import TagTypesSchema
from qikfiller.schemas.lists.types import TypesSchema
from qikfiller.schemas.lists.user import UsersSchema
from qikfiller.utils.date_time import get_start_end, parse_date
from qikfiller.utils.fields import get_field, get_task_field
from qikfiller.utils.validation import (
    validate_date_type, validate_field_collection, validate_limit,
    validate_qik_api_key, validate_qik_api_url,
)


def get_all_rows(session, table):
    return session.query(table).all()


class QikFiller(object):
    """
    Fill out QikTimesheets... Qikker!
    """

    def __init__(self, qik_api_key=None, qik_api_url=None):
        self._session = Session()
        self.qik_api_key = validate_qik_api_key(self._session, qik_api_key)
        self.qik_api_url = validate_qik_api_url(self._session, qik_api_url)

    def _get_data(self, type_):
        response = requests.get(urljoin(self.qik_api_url, '{}.json'.format(type_)),
                                params={'api_key': self.qik_api_key}).json()
        return response

    def init(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        profile = Profile(id=1, qik_api_url=self.qik_api_url, qik_api_key=self.qik_api_key)
        self._session.add(profile)
        self._session.commit()
        self.load()
        return 'Initialisation successful!'

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
        print('Successfully loaded data from {api_url}'.format(api_url=self.qik_api_url))

    def clients(self):
        return get_all_rows(self._session, Client)

    def tasks(self):
        """
        
        """
        tasks = self._session.query(Task) \
            .options(joinedload('client')) \
            .options(joinedload('parent'))
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
        return get_all_rows(self._session, User)

    def categories(self):
        return get_all_rows(self._session, Category)

    def tag_types(self):
        return get_all_rows(self._session, TagType)

    def types(self):
        return get_all_rows(self._session, Type)

    def search(self, start=(date.today() - timedelta(weeks=1)), end=date.today(),
               types=ALL, clients=ALL, tasks=ALL, categories=ALL,
               limit=1000, date_type='created', description=None, jira_id=None, user='apiuser', dry=False):
        """
        http://biarrioptimisation.qiktimes.com/api/v1/entries/search.json
        ?api_key=12345
        &date_range_from=2017-03-15
        &date_range_to=2017-03-26
        &rate=All
        &client=All
        &task=All
        &categories=All
        &users=All
        &limit=1000
        &date_type=created_at
        """

        data = {
            'api_key': self.qik_api_key,
            'date_range_from': parse_date(start).strftime('%Y-%m-%d'),
            'date_range_to': parse_date(end).strftime('%Y-%m-%d'),
            'rate': validate_field_collection(self._session, Type, types),
            'client': validate_field_collection(self._session, Client, clients),
            'task': validate_field_collection(self._session, Task, tasks),
            'categories': validate_field_collection(self._session, Category, categories),
            'users': user,
            'limit': validate_limit(limit),
            'date_type': validate_date_type(date_type),
        }

        if dry:
            return data
        response = requests.get(urljoin(self.qik_api_url, 'entries', 'search.json'), params=data)
        return response.content

    def create(self, type, task, category, start=None, end=None, duration=None, date=0, description="",
               jira_id="", user='apiuser', dry=False):
        date, start, end = get_start_end(date, start, end, duration)
        type = get_field(self._session, Type, type)
        task = get_task_field(self._session, task)
        category = get_field(self._session, Category, category)

        data = {
            'api_key': self.qik_api_key,
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
            response = requests.post(urljoin(self.qik_api_url, 'entries.json'), params=data)
            print(response.url)
            print(response.status_code)
            print(response.content)


def main():
    try:
        fire.Fire(QikFiller)
    except (EOFError, KeyboardInterrupt):
        print('Exiting!')
