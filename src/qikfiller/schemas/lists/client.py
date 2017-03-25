from marshmallow import fields, post_load

from qikfiller.schemas.lists import (
    BaseCollectionObject, BaseCollectionSchema, BaseSchema, register_class,
)
from qikfiller.schemas.lists.task import TaskSchema


class ClientSchema(BaseSchema):
    LOAD_INTO = 'Client'

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    owner_id = fields.Integer(allow_none=True)
    owner_name = fields.String(allow_none=True)
    custom_fields = fields.List(fields.String())
    tasks = fields.Nested(TaskSchema, many=True)

    @post_load
    def to_obj(self, data):
        try:
            data["custom_fields"] = '|'.join(data["custom_fields"])
        except KeyError:
            pass
        return super(ClientSchema, self).to_obj(data)


class ClientsSchema(BaseCollectionSchema):
    LOAD_INTO = 'Clients'

    clients = fields.Nested(ClientSchema, many=True)


@register_class
class Clients(BaseCollectionObject):
    _SCHEMA = ClientsSchema
