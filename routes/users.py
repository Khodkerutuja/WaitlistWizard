from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_service import UserService
from schemas.user_schema import user_schema, user_update_schema
from utils.auth_utils import active_user_required
from flasgger import swag_from

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get user profile',
    'description': 'Get current user profile',
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
            'description': 'User profile'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def get_profile():
    user_id = get_jwt_identity()
    user = UserService.get_user_by_id(user_id)
    
    if not user:
        return jsonify(message="User not found"), 404
    
    result = user_schema.dump(user)
    return jsonify(user=result), 200

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Update user profile',
    'description': 'Update current user profile',
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
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'User profile updated successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate with schema
    errors = user_update_schema.validate(data)
    if errors:
        return jsonify(errors=errors), 400
    
    # Update profile
    updated_user, message = UserService.update_user_profile(user_id, data)
    if not updated_user:
        return jsonify(message=message), 400
    
    result = user_schema.dump(updated_user)
    return jsonify(message=message, user=result), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get user by ID',
    'description': 'Get user by ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'User profile'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def get_user(user_id):
    user = UserService.get_user_by_id(user_id)
    
    if not user:
        return jsonify(message="User not found"), 404
    
    result = user_schema.dump(user)
    return jsonify(user=result), 200

@users_bp.route('/providers', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get all providers',
    'description': 'Get all service providers',
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
            'description': 'List of providers'
        }
    }
})
def get_providers():
    providers = UserService.get_all_providers()
    result = user_schema.dump(providers, many=True)
    return jsonify(providers=result), 200
