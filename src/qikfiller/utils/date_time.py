from datetime import time, datetime, date as date_, timedelta

from dateutil.parser import parse


def parse_time(t):
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


def to_timedelta(t):
    return datetime.combine(date_.min, parse_time(t)) - datetime.min


def parse_date(d):
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