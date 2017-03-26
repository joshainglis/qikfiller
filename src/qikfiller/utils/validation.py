import sys
from os import getenv

from qikfiller.cache.orm import Profile
from qikfiller.constants import ALL, VALID_DATE_TYPES
from qikfiller.utils.fields import get_field


def validate_qik_api_key(session, qik_api_key):
    qik_api_key = qik_api_key if qik_api_key is not None else getenv('QIK_API_KEY')
    if qik_api_key is None:
        try:
            return session.query(Profile).first().qik_api_key
        except AttributeError:
            pass
    if qik_api_key is None:
        print("Please provide your QIK API key")
        sys.exit(1)
    return qik_api_key


def validate_qik_api_url(session, qik_api_url):
    qik_api_url = qik_api_url if qik_api_url is not None else getenv('QIK_API_URL')
    if qik_api_url is None:
        try:
            return session.query(Profile).first().qik_api_url
        except AttributeError:
            pass
    if qik_api_url is None:
        print("Please provide your the url to you QikTimes instance")
        sys.exit(1)
    return qik_api_url


def validate_date_type(date_type):
    if date_type not in VALID_DATE_TYPES:
        raise ValueError(
            'Please enter a valid date type for the date-type option. One of: {}'.format(', '.join(VALID_DATE_TYPES)))
    return '{date_type}_at'.format(date_type=date_type)


def validate_limit(limit):
    limit = int(limit)
    if limit < 1:
        raise ValueError('limit option must be an integer >0')


def validate_field(session, table, field):
    if isinstance(field, int):
        try:
            return session.query(table).get(field).id
        except AttributeError:
            raise ValueError(
                'No {table} with id {field_id}'.format(table=table.__class__.__name__.lower(), field_id=field))
    else:
        return get_field(session, table, field)


def validate_field_collection(session, table, field):
    if isinstance(field, (list, tuple, set)):
        return ','.join(str(validate_field(session, table, f)) for f in field)
    if isinstance(field, str) and (field.lower() == ALL.lower()):
        return ALL
    return validate_field(session, table, field)
