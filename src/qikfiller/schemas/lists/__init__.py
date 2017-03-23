from marshmallow import Schema, post_load

obj_classes = {}


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


class BaseObj(object):
    _SCHEMA = None

    def __init__(self, id, name, **kwargs):
        self.id = id
        self.name = name

        for field in self._keys():
            try:
                setattr(self, field, kwargs[field])
            except KeyError:
                pass

    @classmethod
    def _keys(cls):
        return cls._SCHEMA._declared_fields.keys()

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join('{}={}'.format(x, getattr(self, x)) for x in self._keys() if hasattr(self, x))
        )

    def __str__(self):
        return "{}-{}".format(self.id, self.name)


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
