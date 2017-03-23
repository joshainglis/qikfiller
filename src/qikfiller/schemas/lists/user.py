from marshmallow import fields

from qikfiller.schemas.lists import BaseCollectionObject, BaseCollectionSchema, BaseObj, BaseSchema, obj_classes


class UserSchema(BaseSchema):
    LOAD_INTO = 'User'

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    login = fields.String(required=True)
    time_zone = fields.String(required=True)
    email = fields.Email(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    enabled = fields.Boolean(required=True)
    is_admin = fields.Boolean(required=True)
    updated_at = fields.DateTime(required=True)
    last_login = fields.DateTime(required=True)
    created_at = fields.DateTime(required=True)


class UsersSchema(BaseCollectionSchema):
    LOAD_INTO = 'Users'

    users = fields.Nested(UserSchema, many=True)


class User(BaseObj):
    _SCHEMA = UserSchema


obj_classes['User'] = User


class Users(BaseCollectionObject):
    _SCHEMA = UsersSchema
    pass


obj_classes['Users'] = Users
