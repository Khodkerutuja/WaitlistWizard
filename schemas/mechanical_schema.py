from marshmallow import Schema, fields, validate
from models.mechanical import MechanicalServiceType
from schemas.service_schema import ServiceSchema, ServiceCreateSchema, ServiceUpdateSchema

class MechanicalServiceSchema(ServiceSchema):
    mechanical_type = fields.String(required=True, validate=validate.OneOf([
        MechanicalServiceType.BIKE_REPAIR, MechanicalServiceType.CAR_REPAIR,
        MechanicalServiceType.GENERAL_MAINTENANCE, MechanicalServiceType.BREAKDOWN_ASSISTANCE,
        MechanicalServiceType.TOWING, MechanicalServiceType.OTHER
    ]))
    service_charge = fields.Decimal(as_string=True, required=True)
    additional_charges_desc = fields.String()
    estimated_time = fields.Integer() # in minutes
    offers_pickup = fields.Boolean(default=False)
    pickup_charge = fields.Decimal(as_string=True)

class MechanicalServiceCreateSchema(ServiceCreateSchema):
    mechanical_type = fields.String(required=True, validate=validate.OneOf([
        MechanicalServiceType.BIKE_REPAIR, MechanicalServiceType.CAR_REPAIR,
        MechanicalServiceType.GENERAL_MAINTENANCE, MechanicalServiceType.BREAKDOWN_ASSISTANCE,
        MechanicalServiceType.TOWING, MechanicalServiceType.OTHER
    ]))
    service_charge = fields.Decimal(as_string=True, required=True)
    additional_charges_desc = fields.String()
    estimated_time = fields.Integer() # in minutes
    offers_pickup = fields.Boolean(default=False)
    pickup_charge = fields.Decimal(as_string=True)

class MechanicalServiceUpdateSchema(ServiceUpdateSchema):
    service_charge = fields.Decimal(as_string=True)
    additional_charges_desc = fields.String()
    estimated_time = fields.Integer() # in minutes
    offers_pickup = fields.Boolean()
    pickup_charge = fields.Decimal(as_string=True)

class MechanicalBookingSchema(Schema):
    booking_time = fields.DateTime(required=True)
    vehicle_details = fields.String()
    issue_description = fields.String()
    pickup_required = fields.Boolean(default=False)
    pickup_address = fields.String()
