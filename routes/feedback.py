from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.feedback_service import FeedbackService
from schemas.feedback_schema import feedback_schema, feedbacks_schema, feedback_create_schema
from utils.auth_utils import active_user_required
from flasgger import swag_from

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/service/<int:service_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Get service feedback',
    'description': 'Get all feedback for a service',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'service_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Service ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of feedback'
        }
    }
})
def get_service_feedback(service_id):
    feedbacks = FeedbackService.get_feedback_by_service(service_id)
    result = feedbacks_schema.dump(feedbacks)
    return jsonify(feedbacks=result), 200

@feedback_bp.route('/provider/<int:provider_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Get provider feedback',
    'description': 'Get all feedback for a service provider',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'provider_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Provider ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of feedback'
        }
    }
})
def get_provider_feedback(provider_id):
    feedbacks = FeedbackService.get_feedback_by_provider(provider_id)
    result = feedbacks_schema.dump(feedbacks)
    return jsonify(feedbacks=result), 200

@feedback_bp.route('/user', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Get user feedback',
    'description': 'Get all feedback provided by current user',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of feedback'
        }
    }
})
def get_user_feedback():
    user_id = get_jwt_identity()
    feedbacks = FeedbackService.get_feedback_by_user(user_id)
    result = feedbacks_schema.dump(feedbacks)
    return jsonify(feedbacks=result), 200

@feedback_bp.route('/', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Create feedback',
    'description': 'Create feedback for a service',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'service_id': {'type': 'integer'},
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'review': {'type': 'string'}
                },
                'required': ['service_id', 'rating']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Feedback submitted successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Active user required'
        },
        '404': {
            'description': 'Service not found'
        }
    }
})
def create_feedback():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate with schema
    errors = feedback_create_schema.validate(data)
    if errors:
        return jsonify(errors=errors), 400
    
    service_id = data.get('service_id')
    rating = data.get('rating')
    review = data.get('review')
    
    # Create feedback
    feedback, message = FeedbackService.create_feedback(user_id, service_id, rating, review)
    if not feedback:
        if "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    result = feedback_schema.dump(feedback)
    return jsonify(message=message, feedback=result), 201

@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Update feedback',
    'description': 'Update feedback',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'feedback_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Feedback ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'review': {'type': 'string'}
                },
                'required': ['rating']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Feedback updated successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Not authorized'
        },
        '404': {
            'description': 'Feedback not found'
        }
    }
})
def update_feedback(feedback_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate rating
    rating = data.get('rating')
    if rating is not None and (not isinstance(rating, int) or rating < 1 or rating > 5):
        return jsonify(message="Rating must be between 1 and 5"), 400
    
    # Update feedback
    updated_feedback, message = FeedbackService.update_feedback(user_id, feedback_id, data)
    if not updated_feedback:
        if "not authorized" in message.lower():
            return jsonify(message=message), 403
        elif "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    result = feedback_schema.dump(updated_feedback)
    return jsonify(message=message, feedback=result), 200

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Delete feedback',
    'description': 'Delete feedback',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'feedback_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Feedback ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Feedback deleted successfully'
        },
        '403': {
            'description': 'Not authorized'
        },
        '404': {
            'description': 'Feedback not found'
        }
    }
})
def delete_feedback(feedback_id):
    user_id = get_jwt_identity()
    
    # Delete feedback
    success, message = FeedbackService.delete_feedback(user_id, feedback_id)
    if not success:
        if "not authorized" in message.lower():
            return jsonify(message=message), 403
        elif "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    return jsonify(message=message), 200

@feedback_bp.route('/ratings/service/<int:service_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Get service average rating',
    'description': 'Get average rating for a service',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'service_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Service ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Service average rating'
        }
    }
})
def get_service_rating(service_id):
    avg_rating = FeedbackService.get_service_average_rating(service_id)
    return jsonify(service_id=service_id, average_rating=avg_rating), 200

@feedback_bp.route('/ratings/provider/<int:provider_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Feedback'],
    'summary': 'Get provider average rating',
    'description': 'Get average rating for a service provider',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'provider_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Provider ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Provider average rating'
        }
    }
})
def get_provider_rating(provider_id):
    avg_rating = FeedbackService.get_provider_average_rating(provider_id)
    return jsonify(provider_id=provider_id, average_rating=avg_rating), 200
