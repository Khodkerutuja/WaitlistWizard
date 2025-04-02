from marshmallow import Schema, fields, validate
from models.household import HouseholdServiceType
from schemas.service_schema import ServiceSchema, ServiceCreateSchema, ServiceUpdateSchema

class HouseholdServiceSchema(ServiceSchema):
    household_type = fields.String(required=True, validate=validate.OneOf([
        HouseholdServiceType.MAID, HouseholdServiceType.PLUMBING, 
        HouseholdServiceType.ELECTRICAL, HouseholdServiceType.PEST_CONTROL,
        HouseholdServiceType.CLEANING, HouseholdServiceType.OTHER
    ]))
    hourly_rate = fields.Decimal(as_string=True)
    visit_charge = fields.Decimal(as_string=True)
    estimated_duration = fields.Integer() # in minutes

class HouseholdServiceCreateSchema(ServiceCreateSchema):
    household_type = fields.String(required=True, validate=validate.OneOf([
        HouseholdServiceType.MAID, HouseholdServiceType.PLUMBING, 
        HouseholdServiceType.ELECTRICAL, HouseholdServiceType.PEST_CONTROL,
        HouseholdServiceType.CLEANING, HouseholdServiceType.OTHER
    ]))
    hourly_rate = fields.Decimal(as_string=True)
    visit_charge = fields.Decimal(as_string=True)
    estimated_duration = fields.Integer() # in minutes

class HouseholdServiceUpdateSchema(ServiceUpdateSchema):
    hourly_rate = fields.Decimal(as_string=True)
    visit_charge = fields.Decimal(as_string=True)
    estimated_duration = fields.Integer() # in minutes

class HouseholdBookingSchema(Schema):
    booking_time = fields.DateTime(required=True)
    hours = fields.Decimal(as_string=True)
    address = fields.String()
