from marshmallow import Schema, fields, validate, validates, ValidationError
from models.user import UserRole, UserStatus

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    phone_number = fields.String(required=True, validate=validate.Length(min=6, max=15))
    address = fields.String(validate=validate.Length(max=255))
    role = fields.String(validate=validate.OneOf([UserRole.USER, UserRole.POWER_USER, UserRole.ADMIN]))
    status = fields.String(validate=validate.OneOf([UserStatus.ACTIVE, UserStatus.PENDING, UserStatus.INACTIVE]))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Service Provider specific fields
    service_type = fields.String()
    description = fields.String()
    
    # Additional fields
    wallet = fields.Nested('WalletSchema', exclude=['user_id'], dump_only=True)
    
    @validates('service_type')
    def validate_service_type(self, value):
        # Service type is required for service providers
        if self.context.get('role') == UserRole.POWER_USER and not value:
            raise ValidationError('Service type is required for service providers')

class UserRegistrationSchema(UserSchema):
    password = fields.String(required=True, validate=validate.Length(min=8))
    
    class Meta:
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number', 
                  'address', 'role', 'service_type', 'description')

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class UserUpdateSchema(Schema):
    first_name = fields.String(validate=validate.Length(min=1, max=50))
    last_name = fields.String(validate=validate.Length(min=1, max=50))
    phone_number = fields.String(validate=validate.Length(min=6, max=15))
    address = fields.String(validate=validate.Length(max=255))
    description = fields.String()

class PasswordChangeSchema(Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))
