from marshmallow import Schema, fields, post_load
from typing import List, Mapping


class Task(object):
    __slots__ = ("id", "name", "owner_id", "owner_name", "custom_fields", "sub_tasks", "archived", "estimated_hours")

    def __init__(self, id, name, owner_id=None, owner_name=None, custom_fields=None, sub_tasks=None, archived=None,
                 estimated_hours=None):
        self.owner_name = owner_name
        self.id = id
        self.name = name
        self.owner_id = owner_id
        self.custom_fields = custom_fields
        self.sub_tasks = sub_tasks
        self.archived = archived
        self.estimated_hours = estimated_hours

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__,
                               ', '.join('{}={}'.format(x, getattr(self, x)) for x in self.__slots__))

    def __str__(self):
        return "{}-{}".format(self.id, self.name)


class Tasks(object):
    def __init__(self, tasks: List[Task]):
        tasks = tasks if tasks is not None else []
        self._by_id = {x.id: x for x in tasks}
        self._by_name = {x.name: x for x in tasks}

    def from_id(self, id_):
        return self._by_id[id_]

    def from_name(self, name):
        return self._by_name[name]

    def list_all(self, indent=0):
        for x in self._by_id.values():
            s = '{:<3}: {}'.format(x.id, x.name)
            print('{}{}'.format(' ' * indent, s))
            Tasks(x.sub_tasks).list_all(indent=indent + 2)


class TaskSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    owner_id = fields.Integer(allow_none=True)
    owner_name = fields.String(allow_none=True)
    custom_fields = fields.List(fields.String())
    archived = fields.Boolean()
    estimated_hours = fields.Integer(allow_none=True)
    sub_tasks = fields.Nested('TaskSchema', many=True)

    @post_load
    def make_task(self, data: dict) -> Task:
        return Task(**data)


class TasksSchema(Schema):
    tasks = fields.List(fields.Nested(TaskSchema))

    @post_load
    def make_tasts(self, data: Mapping[str, List[Task]]) -> Tasks:
        return Tasks(data['tasks'])
