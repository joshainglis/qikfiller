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
from qikfiller.utils.fields import get_field
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
        """
        Create a new event.

        Example usage:
        Yesterday we did 2 'Billable' (TYPE id:1) hours of 'Web App Development' (CATEGORY id:31) on the 
        'Resource Planner Feature' (TASK id:27) for 
        'Bob's Teahouse' (Customer id:5) from 10am.
        Long form, this would look like:
        
            qikfiller create --type Billable --task 'Resource Planner Feature' --category 'Web App Development' \
                --date 2017-03-23 --start 10am --duration 2h \
                --description 'Worked on the Bob's Teahouse Resource Planner Feature' \
                --jira-id BTH-123

        But we could also write this in short form to get the same result        

            qikfiller create bill tea:plan app \
                --date -1 --start 10am --duration 2h \
                --description "Worked on the Resource Planner" \
                --jira-id "BTH-302"
        
        If you are entering times as you go and know the ids (from previous usage), this can be shortened significantly:
        
            qikfiller create 1 27 31 10am
        
        Assuming it's now 12:30pm this will create a task from 10am-12:30pm. 
        The 1, 27, 31 are the ids of the TYPE, TASK, CATEGORY from above.    
        
        :param type: Task type, eg Billable, Unbillable. Pass either the id or any part of the string. 
                     You will be prompted if the string is ambiguous
        :type type: str | int
        :param task: The id or name of task that the event refers to. eg 'Resource Planner Feature'.
                     You can put the client name (or part of) in front (separated by a colon) to add specificity, if 
                     needed. For example for task 'Scoping' for client 'Bob's Teahouse' you could enter 'tea:sco'.
        :type task: str | int
        :param category: The id or name of the event category, for example: 'Code Review', 'Web App Development'. 
                         A partial name can be entered
        :type category: str | int
        :param start: Event start time. Can be entered in many ways: eg '10am', '13:30'.
                      Any two of (start, end, duration) can be used: 
                        '--start 10am --end 1pm'
                        '--start 10am --duration 3h'
                        '--end 1pm --duration 3h'
        :type start: str
        :param end: Event end time. Can be entered in many ways: eg '10am', '13:30'
                    Any two of (start, end, duration) can be used: 
                      '--start 10am --end 1pm'
                      '--start 10am --duration 3h'
                      '--end 1pm --duration 3h'
        :type end: str
        :param duration: Duration of the event. Can be entered in many ways: eg '2h', '30m', '1:30'
                         Any two of (start, end, duration) can be used: 
                           '--start 10am --end 1pm'
                           '--start 10am --duration 3h'
                           '--end 1pm --duration 3h'
        :type duration: str
        :param date: Date of the event. Default=today. Can be entered as an integer offset from today, or as a date.
                     eg: '--date -1' is yesterday. 
                         '--date 2feb' is 2nd of February this year 
                         '--date 2017-02-05' is 5th of Feb 2017
        :type date: str | int
        :param description: Event description (optional)
        :type description: str
        :param jira_id: Jira Id (eg ABC-123) that the event refers to (optional)
        :type jira_id: str
        :param user: User to create the event for. Unless you're an admin, this can only be you ('apiuser')
        :type user: str | int
        :param dry: Dry run. Don't actually send the command to the server.
        :type dry: bool
        """
        date, start, end = get_start_end(date, start, end, duration)
        type = get_field(self._session, Type, type)
        task = get_field(self._session, Task, task)
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
