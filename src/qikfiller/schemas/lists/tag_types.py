from marshmallow import fields

from qikfiller.schemas.lists import BaseCollectionObject, BaseCollectionSchema, BaseObj, BaseSchema, register_class


class TagTypeSchema(BaseSchema):
    LOAD_INTO = 'TagType'

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True, allow_none=True)


class TagTypesSchema(BaseCollectionSchema):
    LOAD_INTO = 'TagTypes'
    KEY = 'tag_types'

    tag_types = fields.Nested(TagTypeSchema, many=True)


@register_class
class TagType(BaseObj):
    _SCHEMA = TagTypeSchema


@register_class
class TagTypes(BaseCollectionObject):
    _SCHEMA = TagTypesSchema
