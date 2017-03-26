from marshmallow import Schema, post_load

obj_classes = {}


def register_class(cls):
    obj_classes[cls.__name__] = cls
    return cls


class BaseSchema(Schema):
    LOAD_INTO = None

    @post_load
    def to_obj(self, data):
        return obj_classes[self.LOAD_INTO](**data)


class BaseCollectionSchema(BaseSchema):
    KEY = None

    @post_load
    def to_obj(self, data):
        return obj_classes[self.LOAD_INTO](data[self.KEY if self.KEY is not None else self.LOAD_INTO.lower()])


class BaseCollectionObject(object):
    _SCHEMA = None

    def __init__(self, collection):
        setattr(self, self.__class__.__name__.lower(), collection or [])
        self._by_id = {x.id: x for x in collection}
        self._by_name = {x.name: x for x in collection}

    def from_id(self, id_):
        return self._by_id[id_]

    def from_name(self, name):
        return self._by_name[name]

    def list_all(self):
        return {x.id: x.name for x in self._by_id.values()}
