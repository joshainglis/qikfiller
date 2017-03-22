import sys
from os import getenv
from urllib.parse import urljoin

import fire
import requests

from qikfiller.schemas.lists.client import ClientsSchema

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

    def clients(self, name=None, id=None):
        data = requests.get(urljoin(self.qik_url, 'clients.json'), params={'apikey': self.apikey}).json()
        clients = ClientsSchema().load(data).data
        if name is not None:
            return clients.from_name(name)
        elif id is not None:
            return clients.from_id(id)
        else:
            return clients

    def tasks(self):
        data = requests.get(urljoin(self.qik_url, 'tasks.json'), params={'apikey': self.apikey}).json()
        clients = ClientsSchema().load(data).data
        return clients



def main():
    fire.Fire(QikFiller)
