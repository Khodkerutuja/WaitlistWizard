from marshmallow import fields, validate
from app import ma
from models import MechanicalService
from schemas.service_schema import ServiceSchema

class MechanicalServiceSchema(ServiceSchema):
    class Meta:
        model = MechanicalService
        load_instance = True
    
    service_type = ma.auto_field(required=True)
    vehicle_types = ma.auto_field()

class MechanicalServiceUpdateSchema(MechanicalServiceSchema):
    class Meta:
        model = MechanicalService
        load_instance = True
    
    name = ma.auto_field(validate=validate.Length(min=3, max=100))
    description = ma.auto_field()
    price = ma.auto_field(validate=validate.Range(min=0))
    service_type = ma.auto_field()
    vehicle_types = ma.auto_field()

# Initialize schemas
mechanical_service_schema = MechanicalServiceSchema()
mechanical_services_schema = MechanicalServiceSchema(many=True)
mechanical_service_update_schema = MechanicalServiceUpdateSchema()
