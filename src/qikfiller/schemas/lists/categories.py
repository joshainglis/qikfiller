from marshmallow import fields

from qikfiller.schemas.lists import BaseCollectionObject, BaseCollectionSchema, BaseObj, BaseSchema, obj_classes


class CategorySchema(BaseSchema):
    LOAD_INTO = 'Category'

    id = fields.Integer(required=True)
    name = fields.String(required=True)


class CategoriesSchema(BaseCollectionSchema):
    LOAD_INTO = 'Categories'

    categories = fields.Nested(CategorySchema, many=True)


class Category(BaseObj):
    _SCHEMA = CategorySchema


obj_classes['Category'] = Category


class Categories(BaseCollectionObject):
    _SCHEMA = CategoriesSchema
    pass


obj_classes['Categories'] = Categories
