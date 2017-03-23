from marshmallow import fields

from qikfiller.schemas.lists import BaseCollectionObject, BaseCollectionSchema, BaseObj, BaseSchema, obj_classes


class TaskSchema(BaseSchema):
    LOAD_INTO = 'Task'

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    owner_id = fields.Integer(allow_none=True)
    owner_name = fields.String(allow_none=True)
    custom_fields = fields.List(fields.String())
    archived = fields.Boolean()
    estimated_hours = fields.Integer(allow_none=True)
    sub_tasks = fields.Nested('TaskSchema', many=True)


class TasksSchema(BaseCollectionSchema):
    LOAD_INTO = 'Tasks'

    tasks = fields.List(fields.Nested(TaskSchema))


class Task(BaseObj):
    _SCHEMA = TaskSchema


obj_classes['Task'] = Task


class Tasks(BaseCollectionObject):
    _SCHEMA = TasksSchema

    def list_all(self, indent=0):
        for x in self._by_id.values():
            s = '{:<3}: {}'.format(x.id, x.name)
            print('{}{}'.format(' ' * indent, s))
            Tasks(x.sub_tasks).list_all(indent=indent + 2)


obj_classes['Tasks'] = Tasks
