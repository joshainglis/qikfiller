import sys
from os import getenv

QIK_API_KEY = getenv('QIK_API_KEY')
QIK_URL = getenv('QIK_URL')


def validate_api_key(apikey):
    apikey = apikey if apikey is not None else QIK_API_KEY
    if apikey is None:
        print("Please provide your QIK API key")
        sys.exit(1)
    return apikey


def validate_url(qik_url):
    qik_url = qik_url if qik_url is not None else QIK_URL
    if qik_url is None:
        print("Please provide your the url to you QikTimes instance")
        sys.exit(1)
    return qik_url