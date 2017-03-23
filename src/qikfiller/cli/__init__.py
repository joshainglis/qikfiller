import sys
from os import getenv
from urllib.parse import urljoin

import fire
import requests

from qikfiller.schemas.lists.categories import CategoriesSchema
from qikfiller.schemas.lists.client import ClientsSchema
from qikfiller.schemas.lists.tag_types import TagTypesSchema
from qikfiller.schemas.lists.types import TypesSchema
from qikfiller.schemas.lists.user import UserSchema, UsersSchema

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
        response = requests.get(urljoin(self.qik_url, '{}.json'.format(type_)), params={'apikey': self.apikey}).json()
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

    def test(self):
        return UserSchema._declared_fields


def main():
    fire.Fire(QikFiller)
