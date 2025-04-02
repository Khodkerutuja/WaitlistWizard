from marshmallow import Schema, fields, validate
from models.gym import SubscriptionPlan
from schemas.service_schema import ServiceSchema, ServiceCreateSchema, ServiceUpdateSchema

class GymServiceSchema(ServiceSchema):
    gym_name = fields.String(required=True)
    facility_types = fields.List(fields.String(), required=True)
    operating_hours = fields.Dict(keys=fields.String(), values=fields.String(), required=True)
    trainers_available = fields.Boolean()
    dietician_available = fields.Boolean()
    subscription_plans = fields.Dict(keys=fields.String(), values=fields.Decimal(as_string=True), required=True)

class GymServiceCreateSchema(ServiceCreateSchema):
    gym_name = fields.String(required=True)
    facility_types = fields.List(fields.String(), required=True)
    operating_hours = fields.Dict(keys=fields.String(), values=fields.String(), required=True)
    trainers_available = fields.Boolean(default=False)
    dietician_available = fields.Boolean(default=False)
    subscription_plans = fields.Dict(keys=fields.String(), values=fields.Decimal(as_string=True), required=True)

class GymServiceUpdateSchema(ServiceUpdateSchema):
    gym_name = fields.String()
    facility_types = fields.List(fields.String())
    operating_hours = fields.Dict(keys=fields.String(), values=fields.String())
    trainers_available = fields.Boolean()
    dietician_available = fields.Boolean()
    subscription_plans = fields.Dict(keys=fields.String(), values=fields.Decimal(as_string=True))

class GymSubscriptionSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    gym_service_id = fields.Integer(required=True)
    subscription_plan = fields.String(required=True, validate=validate.OneOf([
        SubscriptionPlan.MONTHLY, SubscriptionPlan.QUARTERLY, SubscriptionPlan.ANNUAL
    ]))
    start_date = fields.DateTime(dump_only=True)
    end_date = fields.DateTime(dump_only=True)
    amount_paid = fields.Decimal(as_string=True, dump_only=True)
    trainer_assigned = fields.String(dump_only=True)
    dietician_assigned = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    
    # Include service details
    gym_service = fields.Nested(GymServiceSchema, only=['id', 'name', 'gym_name'], dump_only=True)

class GymSubscriptionCreateSchema(Schema):
    gym_service_id = fields.Integer(required=True)
    subscription_plan = fields.String(required=True, validate=validate.OneOf([
        SubscriptionPlan.MONTHLY, SubscriptionPlan.QUARTERLY, SubscriptionPlan.ANNUAL
    ]))
    trainer_required = fields.Boolean(default=False)
    dietician_required = fields.Boolean(default=False)
