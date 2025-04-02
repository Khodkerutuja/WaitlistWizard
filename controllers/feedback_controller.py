from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.feedback_service import FeedbackService

feedback_bp = Blueprint('feedback', __name__)
feedback_service = FeedbackService()

@feedback_bp.route('/', methods=['POST'])
@jwt_required()
def add_feedback():
    """
    Add feedback for a service
    ---
    tags:
      - Feedback
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - service_id
            - rating
          properties:
            service_id:
              type: integer
            rating:
              type: integer
              minimum: 1
              maximum: 5
            review:
              type: string
    responses:
      201:
        description: Feedback added successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      404:
        description: Service not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['service_id', 'rating']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate rating
    try:
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rating format'}), 400
    
    try:
        feedback = feedback_service.add_feedback(
            user_id=user_id,
            service_id=data['service_id'],
            rating=rating,
            review=data.get('review')
        )
        
        return jsonify({'message': 'Feedback added successfully', 'feedback': feedback.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/service/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service_feedback(service_id):
    """
    Get feedback for a specific service
    ---
    tags:
      - Feedback
    security:
      - JWT: []
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        description: Service ID
    responses:
      200:
        description: List of feedback for the service
      401:
        description: Unauthorized
      404:
        description: Service not found
    """
    try:
        feedbacks = feedback_service.get_service_feedback(service_id)
        return jsonify([feedback.to_dict() for feedback in feedbacks]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/provider/<int:provider_id>', methods=['GET'])
@jwt_required()
def get_provider_feedback(provider_id):
    """
    Get feedback for a specific service provider
    ---
    tags:
      - Feedback
    security:
      - JWT: []
    parameters:
      - name: provider_id
        in: path
        type: integer
        required: true
        description: Provider ID
    responses:
      200:
        description: List of feedback for the provider
      401:
        description: Unauthorized
      404:
        description: Provider not found
    """
    try:
        feedbacks = feedback_service.get_provider_feedback(provider_id)
        return jsonify([feedback.to_dict() for feedback in feedbacks]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_feedback():
    """
    Get feedback given by the current user
    ---
    tags:
      - Feedback
    security:
      - JWT: []
    responses:
      200:
        description: List of feedback given by the user
      401:
        description: Unauthorized
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    try:
        feedbacks = feedback_service.get_user_feedback(user_id)
        return jsonify([feedback.to_dict() for feedback in feedbacks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
@jwt_required()
def update_feedback(feedback_id):
    """
    Update a feedback
    ---
    tags:
      - Feedback
    security:
      - JWT: []
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
        description: Feedback ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            rating:
              type: integer
              minimum: 1
              maximum: 5
            review:
              type: string
    responses:
      200:
        description: Feedback updated successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not authorized to update this feedback
      404:
        description: Feedback not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    data = request.get_json()
    
    # Validate rating if provided
    if 'rating' in data:
        try:
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid rating format'}), 400
    
    try:
        feedback = feedback_service.update_feedback(
            feedback_id=feedback_id,
            user_id=user_id,
            rating=data.get('rating'),
            review=data.get('review')
        )
        
        return jsonify({'message': 'Feedback updated successfully', 'feedback': feedback.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(feedback_id):
    """
    Delete a feedback
    ---
    tags:
      - Feedback
    security:
      - JWT: []
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
        description: Feedback ID
    responses:
      200:
        description: Feedback deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not authorized to delete this feedback
      404:
        description: Feedback not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    role = identity['role']
    
    try:
        feedback_service.delete_feedback(feedback_id, user_id, role)
        
        return jsonify({'message': 'Feedback deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500
