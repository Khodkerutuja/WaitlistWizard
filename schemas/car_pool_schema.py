from marshmallow import fields, validate
from app import ma
from models import CarPoolService
from schemas.service_schema import ServiceSchema

class CarPoolServiceSchema(ServiceSchema):
    class Meta:
        model = CarPoolService
        load_instance = True
    
    vehicle_type = ma.auto_field(required=True)
    vehicle_model = ma.auto_field()
    capacity = ma.auto_field(required=True, validate=validate.Range(min=1))
    available_seats = ma.auto_field(required=True, validate=validate.Range(min=0))
    source = ma.auto_field(required=True)
    destination = ma.auto_field(required=True)
    departure_time = ma.auto_field(required=True)

class CarPoolServiceUpdateSchema(CarPoolServiceSchema):
    class Meta:
        model = CarPoolService
        load_instance = True
    
    name = ma.auto_field(validate=validate.Length(min=3, max=100))
    description = ma.auto_field()
    price = ma.auto_field(validate=validate.Range(min=0))
    vehicle_type = ma.auto_field()
    vehicle_model = ma.auto_field()
    capacity = ma.auto_field(validate=validate.Range(min=1))
    available_seats = ma.auto_field(validate=validate.Range(min=0))
    source = ma.auto_field()
    destination = ma.auto_field()
    departure_time = ma.auto_field()

# Initialize schemas
car_pool_service_schema = CarPoolServiceSchema()
car_pool_services_schema = CarPoolServiceSchema(many=True)
car_pool_service_update_schema = CarPoolServiceUpdateSchema()
