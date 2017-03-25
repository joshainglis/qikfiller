from marshmallow import fields, post_load

from qikfiller.schemas.lists import (
    BaseCollectionObject, BaseCollectionSchema, BaseSchema, register_class,
)


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

    @post_load
    def to_obj(self, data):
        try:
            data["custom_fields"] = '|'.join(data["custom_fields"])
        except KeyError:
            pass
        return super(TaskSchema, self).to_obj(data)


class TasksSchema(BaseCollectionSchema):
    LOAD_INTO = 'Tasks'

    tasks = fields.List(fields.Nested(TaskSchema))


@register_class
class Tasks(BaseCollectionObject):
    _SCHEMA = TasksSchema

    def list_all(self, indent=0):
        for x in self._by_id.values():
            s = '{:<3}: {}'.format(x.id, x.name)
            print('{}{}'.format(' ' * indent, s))
            Tasks(x.sub_tasks).list_all(indent=indent + 2)
