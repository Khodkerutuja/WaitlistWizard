from marshmallow import fields, validate
from app import ma
from models import Feedback

class FeedbackSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Feedback
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    service_id = ma.auto_field(required=True)
    user_id = ma.auto_field(dump_only=True)
    provider_id = ma.auto_field(dump_only=True)
    rating = ma.auto_field(required=True, validate=validate.Range(min=1, max=5))
    review = ma.auto_field()
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    # Include user and service details for display
    username = fields.String(dump_only=True)
    service_name = fields.String(dump_only=True)

class FeedbackCreateSchema(ma.Schema):
    service_id = fields.Integer(required=True)
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    review = fields.String()

# Initialize schemas
feedback_schema = FeedbackSchema()
feedbacks_schema = FeedbackSchema(many=True)
feedback_create_schema = FeedbackCreateSchema()
