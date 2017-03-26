from datetime import date, datetime, time, timedelta

from dateutil.parser import parse


def parse_time(t):
    if isinstance(t, time):
        return t
    if isinstance(t, datetime):
        # noinspection PyArgumentList
        return t.time()
    if isinstance(t, int):
        return time(t)
    try:
        return parse(t).time()
    except:
        raise ValueError('Could not parse {} as a time'.format(t))


def to_timedelta(t):
    return datetime.combine(date.min, parse_time(t)) - datetime.min


def parse_date(d):
    if isinstance(d, date):
        return d
    if isinstance(d, datetime):
        # noinspection PyArgumentList
        return d.date()
    try:
        return parse(d)
    except (ValueError, TypeError):
        pass
    if isinstance(d, int):
        return date.today() + timedelta(days=d)
    raise ValueError('Could not parse {} as a date'.format(d))


def get_start_end(date_, start, end, duration):
    if start and not any([date_, end, duration]):
        end = datetime.now().time()
    date_ = parse_date(date_)
    if start and end:
        start = parse_time(start)
        end = parse_time(end)
    elif start and duration:
        start = parse_time(start)
        end = (datetime.combine(date_, start) + to_timedelta(parse_time(duration))).time()
    elif end and duration:
        end = parse_time(end)
        start = (datetime.combine(date_, end) - to_timedelta(parse_time(duration))).time()
    else:
        raise ValueError("Please provide any two of start, end, duration")
    if start > end:
        raise ValueError('Start time {start} is after end time {end}.'.format(start=start, end=end))
    return date_, start, end
