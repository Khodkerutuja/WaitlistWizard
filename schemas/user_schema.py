from marshmallow import fields, validate
from app import ma
from models import User, UserRole, UserStatus

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True, validate=validate.Length(min=3, max=64))
    email = ma.auto_field(required=True, validate=validate.Email())
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6))
    role = fields.Enum(UserRole, by_value=True, dump_only=True)
    status = fields.Enum(UserStatus, by_value=True, dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)

class UserLoginSchema(ma.Schema):
    email = fields.String(required=True, validate=validate.Email())
    password = fields.String(required=True, validate=validate.Length(min=6))

class UserUpdateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
    
    username = ma.auto_field(validate=validate.Length(min=3, max=64))
    email = ma.auto_field(validate=validate.Email())
    password = fields.String(load_only=True, validate=validate.Length(min=6))

class UserRoleUpdateSchema(ma.Schema):
    role = fields.Enum(UserRole, by_value=True, required=True)

class UserStatusUpdateSchema(ma.Schema):
    status = fields.Enum(UserStatus, by_value=True, required=True)

# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_login_schema = UserLoginSchema()
user_update_schema = UserUpdateSchema()
user_role_update_schema = UserRoleUpdateSchema()
user_status_update_schema = UserStatusUpdateSchema()
