from marshmallow import Schema, fields, validate

class FeedbackSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    provider_id = fields.Integer(dump_only=True)
    service_id = fields.Integer(required=True)
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    review = fields.String()
    created_at = fields.DateTime(dump_only=True)
    
    # Include user and service details
    user = fields.Nested('UserSchema', only=['id', 'first_name', 'last_name'], dump_only=True)
    service = fields.Nested('ServiceSchema', only=['id', 'name', 'service_type'], dump_only=True)

class FeedbackCreateSchema(Schema):
    service_id = fields.Integer(required=True)
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    review = fields.String()

class FeedbackUpdateSchema(Schema):
    rating = fields.Integer(validate=validate.Range(min=1, max=5))
    review = fields.String()
