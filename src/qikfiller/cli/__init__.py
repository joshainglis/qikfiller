import sys
from datetime import date as date_, datetime, time, timedelta
from os import getenv
from urllib.parse import urljoin

import fire
import requests
from dateutil.parser import parse

from qikfiller.schemas.lists.categories import CategoriesSchema
from qikfiller.schemas.lists.client import ClientsSchema
from qikfiller.schemas.lists.tag_types import TagTypesSchema
from qikfiller.schemas.lists.types import TypesSchema
from qikfiller.schemas.lists.user import UsersSchema

QIK_API_KEY = getenv('QIK_API_KEY')
QIK_URL = getenv('QIK_URL')


class QikFiller(object):
    def __init__(self, apikey=None, qik_url=None):
        self.apikey = self._validate_api_key(apikey)
        self.qik_url = self._validate_url(qik_url)

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

    def clients(self, name=None, id=None):
        data = self._get_data('clients')
        clients = ClientsSchema(strict=True).load(data).data
        if name is not None:
            return clients.from_name(name)
        elif id is not None:
            return clients.from_id(id)
        else:
            return clients

    def tasks(self):
        data = self._get_data('tasks')
        clients = ClientsSchema(strict=True).load(data).data
        return clients

    def users(self):
        data = self._get_data('users')
        users = UsersSchema(strict=True).load(data).data
        return users

    def categories(self):
        data = self._get_data('categories')
        categories = CategoriesSchema(strict=True).load(data).data
        return categories

    def tag_types(self):
        data = self._get_data('tag_types')
        tag_types = TagTypesSchema(strict=True).load(data).data
        return tag_types

    def types(self):
        data = self._get_data('types')
        types = TypesSchema(strict=True).load(data).data
        return types

    def _parse_date(self, d):
        if isinstance(d, date_):
            return d
        if isinstance(d, datetime):
            return d.date()
        try:
            return parse(d)
        except (ValueError, TypeError):
            pass
        if isinstance(d, int):
            return date_.today() + timedelta(days=d)
        raise ValueError('Could not parse {} as a date'.format(d))

    def _parse_time(self, t):
        if isinstance(t, time):
            return t
        if isinstance(t, datetime):
            return t.time()
        if isinstance(t, int):
            return time(t)
        try:
            return parse(t).time()
        except:
            raise ValueError('Could not parse {} as a time'.format(t))

    def _to_timedelta(self, t):
        return datetime.combine(date_.min, self._parse_time(t)) - datetime.min

    def create(self, type_id, task_id, category_id, start=None, end=None, duration=None, date=0, description="",
               jira_id="",
               user='apiuser'):
        date = self._parse_date(date)
        if start and end:
            start = self._parse_time(start)
            end = self._parse_time(end)
        elif start and duration:
            start = self._parse_time(start)
            end = (datetime.combine(date, start) + self._to_timedelta(self._parse_time(duration))).time()
        elif end and duration:
            end = self._parse_time(end)
            start = (datetime.combine(date, end) - self._to_timedelta(self._parse_time(duration))).time()
        else:
            raise ValueError("Please provide any two of start, end, duration")
        if start > end:
            raise ValueError('Start time {} is after end time {}.'.format(start, end))

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

        response = requests.post(urljoin(self.qik_url, 'entries.json'), params=data)
        print(response.url)
        print(response.status_code)
        print(response.content)


def main():
    fire.Fire(QikFiller)
