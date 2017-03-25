from marshmallow import fields

from qikfiller.schemas.lists import (
    BaseCollectionObject, BaseCollectionSchema, BaseSchema, register_class,
)


class CategorySchema(BaseSchema):
    LOAD_INTO = 'Category'

    id = fields.Integer(required=True)
    name = fields.String(required=True)


class CategoriesSchema(BaseCollectionSchema):
    LOAD_INTO = 'Categories'

    categories = fields.Nested(CategorySchema, many=True)


@register_class
class Categories(BaseCollectionObject):
    _SCHEMA = CategoriesSchema
