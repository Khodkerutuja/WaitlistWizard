from marshmallow import fields, validate
from app import ma
from models import GymService
from schemas.service_schema import ServiceSchema

class GymServiceSchema(ServiceSchema):
    class Meta:
        model = GymService
        load_instance = True
    
    gym_name = ma.auto_field(required=True)
    service_type = ma.auto_field(required=True)
    trainer_name = ma.auto_field()
    monthly_price = ma.auto_field(required=True, validate=validate.Range(min=0))
    quarterly_price = ma.auto_field(required=True, validate=validate.Range(min=0))
    annual_price = ma.auto_field(required=True, validate=validate.Range(min=0))

class GymServiceUpdateSchema(GymServiceSchema):
    class Meta:
        model = GymService
        load_instance = True
    
    name = ma.auto_field(validate=validate.Length(min=3, max=100))
    description = ma.auto_field()
    price = ma.auto_field(validate=validate.Range(min=0))
    gym_name = ma.auto_field()
    service_type = ma.auto_field()
    trainer_name = ma.auto_field()
    monthly_price = ma.auto_field(validate=validate.Range(min=0))
    quarterly_price = ma.auto_field(validate=validate.Range(min=0))
    annual_price = ma.auto_field(validate=validate.Range(min=0))

# Initialize schemas
gym_service_schema = GymServiceSchema()
gym_services_schema = GymServiceSchema(many=True)
gym_service_update_schema = GymServiceUpdateSchema()
