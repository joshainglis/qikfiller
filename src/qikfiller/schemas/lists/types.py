from marshmallow import fields

from qikfiller.schemas.lists import (
    BaseCollectionObject, BaseCollectionSchema, BaseObj, BaseSchema, register_class,
)


class TypeSchema(BaseSchema):
    LOAD_INTO = 'Type'

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    colour = fields.String(required=True)
    enabled = fields.Boolean(required=True)
    user_creatable = fields.Boolean(required=True)


class TypesSchema(BaseCollectionSchema):
    LOAD_INTO = 'Types'
    KEY = 'types'

    types = fields.Nested(TypeSchema, many=True)


@register_class
class Type(BaseObj):
    _SCHEMA = TypeSchema


@register_class
class Types(BaseCollectionObject):
    _SCHEMA = TypesSchema
