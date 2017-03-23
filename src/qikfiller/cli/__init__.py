import sys
from datetime import date as date_, datetime, time, timedelta
from os import getenv
from urllib.parse import urljoin, urlencode, quote

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

    def create(self, type_id, task_id, category_id, start=None, end=None, duration=None, date=0, description=None,
               jira_id=None,
               user='apiuser'):
        """
        http://biarrioptimisation.qiktimes.com/api/v1/entries.json?
            api_key=4f393a15ab80a6a28cb6d8a8da1ae7c3aa3ff5bf
            &entry[start_time]=2017-03-21%2010:30
            &entry[end_time]=2017-03-21%2013:15
            &entry[type_id]=1
            &entry[task_id]=432
            &entry[category_id]=31
            &entry[owner_id]=apiuser
            &entry[description]=This%20is%20ia%20test
            &entry[jira_id]=QGC-988
        """
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
        if start > end:
            raise ValueError('Start time {} is after end time {}.'.format(start, end))

        print(f'{date} {start} {end}')

        data = {
            'api_key': self.apikey,
            'entry[start_time]': datetime.combine(date, start).strftime("%Y-%m-%d %H:%M"),
            'entry[end_time]': datetime.combine(date, end).strftime("%Y-%m-%d %H:%M"),
            'entry[type_id]': type_id,
            'entry[task_id]': task_id,
            'entry[category_id]': category_id,
            'entry[owner_id]': user,
        }
        if description is not None:
            data['description'] = description
        if jira_id is not None:
            data['jira_id'] = jira_id

        # params = quote('&'.join(f'{k}={v}' for k, v in data.items()).encode())

        # print(urlencode(data))

        response = requests.post(urljoin(self.qik_url, 'entries.json'), params=data)
        print(response.url)
        print(response.status_code)
        print(response.content)


def main():
    fire.Fire(QikFiller)

#                                                            apikey=e8ccb2a55a2df82544e6f914e014768375d042a3&entry%5Bstart_time%5D=2017-03-22%252021%253A30&entry%5Bend_time%5D=2017-03-22%252022%253A00&entry%5Btype_id%5D=1&entry%5Btask_id%5D=432&entry%5Bcategory_id%5D=31&entry%5Bowner_id%5D=apiuser
# http://biarrioptimisation.qiktimes.com/api/v1/entries.json?apikey=e8ccb2a55a2df82544e6f914e014768375d042a3&entry%5Bstart_time%5D=2017-03-22%252021%3A30&entry%5Bend_time%5D=2017-03-22%252022%3A00&entry%5Btype_id%5D=1&entry%5Btask_id%5D=432&entry%5Bcategory_id%5D=31&entry%5Bowner_id%5D=apiuser
# http://biarrioptimisation.qiktimes.com/api/v1/entries.json?apikey=e8ccb2a55a2df82544e6f914e014768375d042a3&entry%5Bstart_time%5D=2017-03-22+21%3A30&entry%5Bend_time%5D=2017-03-22+22%3A00&entry%5Btype_id%5D=1&entry%5Btask_id%5D=432&entry%5Bcategory_id%5D=31&entry%5Bowner_id%5D=apiuser
# http://biarrioptimisation.qiktimes.com/api/v1/entries.json?api_key=&entry%5Bstart_time%5D=2017-03-02%2009:00&entry%5Bend_time%5D=2017-03-02%2009:15&entry%5Btype_id%5D=2&entry%5Btask_id%5D=6&entry%5Bcategory_id%5D=7&entry%5Bdescription%5D=Daily
#                                                            apikey=e8ccb2a55a2df82544e6f914e014768375d042a3&entry%5Bstart_time%5D=2017-03-22+21%3A30&entry%5Bend_time%5D=2017-03-22+22%3A00&entry%5Btype_id%5D=1&entry%5Btask_id%5D=432&entry%5Bcategory_id%5D=31&entry%5Bowner_id%5D=apiuser
#                                                            apikey=e8ccb2a55a2df82544e6f914e014768375d042a3&entry%5Bstart_time%5D=2017-03-22%252021%253A30&entry%5Bend_time%5D=2017-03-22%252022%253A00&entry%5Btype_id%5D=1&entry%5Btask_id%5D=432&entry%5Bcategory_id%5D=31&entry%5Bowner_id%5D=apiuser
#                                                        b%27apikey%27%3Db%27e8ccb2a55a2df82544e6f914e014768375d042a3%27%26b%27entry%5Bstart_time%5D%27%3D2017-03-22%252021%253A30%26b%27entry%5Bend_time%5D%27%3D2017-03-22%252022%253A00%26b%27entry%5Btype_id%5D%27%3D1%26b%27entry%5Btask_id%5D%27%3D432%26b%27entry%5Bcategory_id%5D%27%3D31%26b%27entry%5Bowner_id%5D%27%3Db%27apiuser%27
#                                                            apikey%3De8ccb2a55a2df82544e6f914e014768375d042a3%26entry%5Bstart_time%5D%3D2017-03-22%252021%253A30%26entry%5Bend_time%5D%3D2017-03-22%252022%253A00%26entry%5Btype_id%5D%3D1%26entry%5Btask_id%5D%3D432%26entry%5Bcategory_id%5D%3D31%26entry%5Bowner_id%5D%3Dapiuser
