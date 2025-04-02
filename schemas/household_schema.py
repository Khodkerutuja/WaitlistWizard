from marshmallow import fields, validate
from app import ma
from models import HouseholdService
from schemas.service_schema import ServiceSchema

class HouseholdServiceSchema(ServiceSchema):
    class Meta:
        model = HouseholdService
        load_instance = True
    
    service_type = ma.auto_field(required=True)
    visiting_hours = ma.auto_field()

class HouseholdServiceUpdateSchema(HouseholdServiceSchema):
    class Meta:
        model = HouseholdService
        load_instance = True
    
    name = ma.auto_field(validate=validate.Length(min=3, max=100))
    description = ma.auto_field()
    price = ma.auto_field(validate=validate.Range(min=0))
    service_type = ma.auto_field()
    visiting_hours = ma.auto_field()

# Initialize schemas
household_service_schema = HouseholdServiceSchema()
household_services_schema = HouseholdServiceSchema(many=True)
household_service_update_schema = HouseholdServiceUpdateSchema()
