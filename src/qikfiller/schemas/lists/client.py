from marshmallow import fields

from qikfiller.schemas.lists import BaseCollectionObject, BaseCollectionSchema, BaseObj, BaseSchema, obj_classes
from qikfiller.schemas.lists.task import TaskSchema


class ClientSchema(BaseSchema):
    LOAD_INTO = 'Client'

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    owner_id = fields.Integer(allow_none=True)
    owner_name = fields.String(allow_none=True)
    custom_fields = fields.List(fields.String())
    tasks = fields.Nested(TaskSchema, many=True)


class ClientsSchema(BaseCollectionSchema):
    LOAD_INTO = 'Clients'

    clients = fields.Nested(ClientSchema, many=True)


class Client(BaseObj):
    _SCHEMA = ClientSchema

    def __init__(self, id, name, tasks=None, **kwargs):
        super().__init__(id, name, **kwargs)
        self.tasks = obj_classes['Tasks'](tasks) if tasks is not None else None


obj_classes['Client'] = Client


class Clients(BaseCollectionObject):
    _SCHEMA = ClientsSchema
    pass


obj_classes['Clients'] = Clients
