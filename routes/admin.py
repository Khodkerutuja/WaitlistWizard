from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.auth_service import AuthService
from services.user_service import UserService
from schemas.user_schema import users_schema, user_schema, user_role_update_schema, user_status_update_schema
from utils.auth_utils import admin_required
from models import UserRole, UserStatus
from flasgger import swag_from

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/providers/pending', methods=['GET'])
@jwt_required()
@admin_required()
@swag_from({
    'tags': ['Admin'],
    'summary': 'Get pending providers',
    'description': 'Get all service providers with pending approval',
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
            'description': 'List of pending providers'
        },
        '403': {
            'description': 'Admin access required'
        }
    }
})
def get_pending_providers():
    providers = UserService.get_pending_providers()
    result = users_schema.dump(providers)
    return jsonify(providers=result), 200

@admin_bp.route('/providers/approve/<int:provider_id>', methods=['PUT'])
@jwt_required()
@admin_required()
@swag_from({
    'tags': ['Admin'],
    'summary': 'Approve provider',
    'description': 'Approve a pending service provider',
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
            'description': 'Provider approved successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Admin access required'
        },
        '404': {
            'description': 'Provider not found'
        }
    }
})
def approve_provider(provider_id):
    from flask_jwt_extended import get_jwt_identity
    admin_id = get_jwt_identity()
    
    success, message = AuthService.approve_provider(admin_id, provider_id)
    if not success:
        return jsonify(message=message), 400
    
    return jsonify(message=message), 200

@admin_bp.route('/providers/deactivate/<int:provider_id>', methods=['PUT'])
@jwt_required()
@admin_required()
@swag_from({
    'tags': ['Admin'],
    'summary': 'Deactivate provider',
    'description': 'Deactivate an active service provider',
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
            'description': 'Provider deactivated successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Admin access required'
        },
        '404': {
            'description': 'Provider not found'
        }
    }
})
def deactivate_provider(provider_id):
    from flask_jwt_extended import get_jwt_identity
    admin_id = get_jwt_identity()
    
    success, message = AuthService.deactivate_provider(admin_id, provider_id)
    if not success:
        return jsonify(message=message), 400
    
    return jsonify(message=message), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
@swag_from({
    'tags': ['Admin'],
    'summary': 'Get all users',
    'description': 'Get all users in the system',
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
            'description': 'List of users'
        },
        '403': {
            'description': 'Admin access required'
        }
    }
})
def get_all_users():
    users = UserService.get_all_users()
    result = users_schema.dump(users)
    return jsonify(users=result), 200

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required()
@swag_from({
    'tags': ['Admin'],
    'summary': 'Update user role',
    'description': 'Update a user\'s role',
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
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'role': {'type': 'string', 'enum': ['user', 'power_user', 'admin']}
                },
                'required': ['role']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'User role updated successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Admin access required'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def update_user_role(user_id):
    from flask_jwt_extended import get_jwt_identity
    admin_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    role_str = data.get('role')
    
    # Validate role
    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify(message="Invalid role"), 400
    
    # Update role
    updated_user, message = UserService.update_user_role(admin_id, user_id, role)
    if not updated_user:
        return jsonify(message=message), 400
    
    result = user_schema.dump(updated_user)
    return jsonify(message=message, user=result), 200

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@admin_required()
@swag_from({
    'tags': ['Admin'],
    'summary': 'Update user status',
    'description': 'Update a user\'s status',
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
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['pending', 'active', 'inactive']}
                },
                'required': ['status']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'User status updated successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Admin access required'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def update_user_status(user_id):
    from flask_jwt_extended import get_jwt_identity
    admin_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    status_str = data.get('status')
    
    # Validate status
    try:
        status = UserStatus(status_str)
    except ValueError:
        return jsonify(message="Invalid status"), 400
    
    # Update status
    updated_user, message = UserService.update_user_status(admin_id, user_id, status)
    if not updated_user:
        return jsonify(message=message), 400
    
    result = user_schema.dump(updated_user)
    return jsonify(message=message, user=result), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
@swag_from({
    'tags': ['Admin'],
    'summary': 'Delete user',
    'description': 'Delete a user',
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
            'description': 'User deleted successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Admin access required'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def delete_user(user_id):
    from flask_jwt_extended import get_jwt_identity
    admin_id = get_jwt_identity()
    
    success, message = UserService.delete_user(admin_id, user_id)
    if not success:
        return jsonify(message=message), 400
    
    return jsonify(message=message), 200
