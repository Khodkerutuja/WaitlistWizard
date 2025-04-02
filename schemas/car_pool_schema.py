from marshmallow import Schema, fields, validate, validates, ValidationError
from models.car_pool import VehicleType
from schemas.service_schema import ServiceSchema, ServiceCreateSchema, ServiceUpdateSchema

class CarPoolServiceSchema(ServiceSchema):
    vehicle_type = fields.String(required=True, validate=validate.OneOf([VehicleType.CAR, VehicleType.BIKE]))
    source = fields.String(required=True)
    destination = fields.String(required=True)
    departure_time = fields.DateTime(required=True)
    total_seats = fields.Integer(required=True, validate=validate.Range(min=1))
    available_seats = fields.Integer(dump_only=True)
    vehicle_model = fields.String()
    vehicle_number = fields.String()
    
    @validates('total_seats')
    def validate_total_seats(self, value):
        if self.context.get('vehicle_type') == VehicleType.BIKE and value > 2:
            raise ValidationError('Bikes cannot have more than 2 seats')

class CarPoolServiceCreateSchema(ServiceCreateSchema):
    vehicle_type = fields.String(required=True, validate=validate.OneOf([VehicleType.CAR, VehicleType.BIKE]))
    source = fields.String(required=True)
    destination = fields.String(required=True)
    departure_time = fields.DateTime(required=True)
    total_seats = fields.Integer(required=True, validate=validate.Range(min=1))
    vehicle_model = fields.String()
    vehicle_number = fields.String()

class CarPoolServiceUpdateSchema(ServiceUpdateSchema):
    source = fields.String()
    destination = fields.String()
    departure_time = fields.DateTime()
    total_seats = fields.Integer(validate=validate.Range(min=1))
    vehicle_model = fields.String()
    vehicle_number = fields.String()

class CarPoolBookingSchema(Schema):
    num_seats = fields.Integer(required=True, validate=validate.Range(min=1))
