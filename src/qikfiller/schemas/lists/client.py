from marshmallow import Schema, fields, post_load
from typing import List, Mapping

from qikfiller.schemas.lists.task import TaskSchema, Tasks


class Client(object):
    __slots__ = ("id", "name", "owner_id", "owner_name", "custom_fields", 'tasks')

    def __init__(self, id, name, owner_id=None, owner_name=None, custom_fields=None, tasks=None):
        self.owner_name = owner_name
        self.id = id
        self.name = name
        self.owner_id = owner_id
        self.custom_fields = custom_fields
        self.tasks = Tasks(tasks) if tasks is not None else None

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__,
                               ', '.join('{}={}'.format(x, getattr(self, x)) for x in self.__slots__))

    def __str__(self):
        return "{}-{}".format(self.id, self.name)


class Clients(object):
    def __init__(self, clients: List[Client]):
        self._clients_by_id = {x.id: x for x in clients}
        self._clients_by_name = {x.name: x for x in clients}

    def from_id(self, id_):
        return self._clients_by_id[id_]

    def from_name(self, name):
        return self._clients_by_name[name]

    def list_all(self):
        return {x.id: x.name for x in self._clients_by_id.values()}


class ClientSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    owner_id = fields.Integer(allow_none=True)
    owner_name = fields.String(allow_none=True)
    custom_fields = fields.List(fields.String())
    tasks = fields.Nested(TaskSchema, many=True)

    @post_load
    def make_client(self, data: dict) -> Client:
        return Client(**data)


class ClientsSchema(Schema):
    clients = fields.List(fields.Nested(ClientSchema))

    @post_load
    def make_clients(self, data: Mapping[str, List[Client]]) -> Clients:
        return Clients(data['clients'])
