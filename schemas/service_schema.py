from marshmallow import Schema, fields, validate, validates, ValidationError
from models.service import ServiceType, ServiceStatus, BookingStatus

class ServiceSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    description = fields.String(validate=validate.Length(max=1000))
    provider_id = fields.Integer(dump_only=True)
    service_type = fields.String(required=True, validate=validate.OneOf([
        ServiceType.CAR_POOL, ServiceType.BIKE_POOL, ServiceType.GYM_FITNESS,
        ServiceType.HOUSEHOLD, ServiceType.MECHANICAL
    ]))
    price = fields.Decimal(as_string=True, required=True)
    status = fields.String(dump_only=True)
    location = fields.String()
    availability = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Include provider details
    provider = fields.Nested('UserSchema', only=['id', 'first_name', 'last_name', 'phone_number'], dump_only=True)
    
    # Include average rating
    average_rating = fields.Method('get_average_rating', dump_only=True)
    
    def get_average_rating(self, obj):
        from models.feedback import Feedback
        return Feedback.get_average_rating(obj.provider_id)

class ServiceCreateSchema(ServiceSchema):
    class Meta:
        exclude = ('provider', 'average_rating')

class ServiceUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=3, max=100))
    description = fields.String(validate=validate.Length(max=1000))
    price = fields.Decimal(as_string=True)
    status = fields.String(validate=validate.OneOf([
        ServiceStatus.AVAILABLE, ServiceStatus.UNAVAILABLE
    ]))
    location = fields.String()
    availability = fields.String()

class BookingSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    service_id = fields.Integer(required=True)
    booking_time = fields.DateTime(required=True)
    status = fields.String(dump_only=True)
    amount = fields.Decimal(as_string=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    additional_data = fields.String(dump_only=True)
    
    # Include service and user details
    service = fields.Nested(ServiceSchema, only=['id', 'name', 'service_type'], dump_only=True)
    user = fields.Nested('UserSchema', only=['id', 'first_name', 'last_name', 'phone_number'], dump_only=True)

class BookingCreateSchema(Schema):
    service_id = fields.Integer(required=True)
    booking_time = fields.DateTime(required=True)
    # Additional fields can be included based on service type

class BookingStatusUpdateSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf([
        BookingStatus.CONFIRMED, BookingStatus.REJECTED, BookingStatus.COMPLETED
    ]))
