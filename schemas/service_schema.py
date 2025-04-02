from marshmallow import fields, validate
from app import ma
from models import Service, ServiceCategory, ServiceStatus

class ServiceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Service
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True, validate=validate.Length(min=3, max=100))
    description = ma.auto_field()
    category = fields.Enum(ServiceCategory, by_value=True, required=True)
    price = ma.auto_field(required=True, validate=validate.Range(min=0))
    provider_id = ma.auto_field(dump_only=True)
    status = fields.Enum(ServiceStatus, by_value=True, dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    # Provider details
    provider_name = fields.String(dump_only=True)
    provider_email = fields.String(dump_only=True)
    
    # Average rating
    average_rating = fields.Float(dump_only=True)
    
    # Type-specific fields
    type = fields.String(dump_only=True)

class ServiceUpdateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Service
        load_instance = True
    
    name = ma.auto_field(validate=validate.Length(min=3, max=100))
    description = ma.auto_field()
    price = ma.auto_field(validate=validate.Range(min=0))
    status = fields.Enum(ServiceStatus, by_value=True)

# Initialize schemas
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
service_update_schema = ServiceUpdateSchema()
