from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from schemas.user_schema import user_schema, user_login_schema
from utils.validation import is_valid_email, is_valid_password
from models import UserRole
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Register a new user',
    'description': 'Create a new user account',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'role': {'type': 'string', 'enum': ['user', 'power_user']}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'User registered successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '409': {
            'description': 'User already exists'
        }
    }
})
def register():
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role_str = data.get('role', 'user')
    
    # Validate required fields
    if not username or not email or not password:
        return jsonify(message="Missing required fields"), 400
    
    # Validate email format
    if not is_valid_email(email):
        return jsonify(message="Invalid email format"), 400
    
    # Validate password strength
    if not is_valid_password(password):
        return jsonify(message="Password must be at least 6 characters"), 400
    
    # Validate role
    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify(message="Invalid role"), 400
    
    # Register user
    user, message = AuthService.register_user(username, email, password, role)
    if not user:
        return jsonify(message=message), 409
    
    # Return user data
    result = user_schema.dump(user)
    return jsonify(message=message, user=result), 201

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Login user',
    'description': 'Authenticate and login a user',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Login successful'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '401': {
            'description': 'Authentication failed'
        }
    }
})
def login():
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Validate required fields
    if not email or not password:
        return jsonify(message="Missing required fields"), 400
    
    # Login user
    result, message = AuthService.login_user(email, password)
    if not result:
        return jsonify(message=message), 401
    
    return jsonify(message=message, **result), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Change password',
    'description': 'Change user password',
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
                    'current_password': {'type': 'string'},
                    'new_password': {'type': 'string'}
                },
                'required': ['current_password', 'new_password']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Password changed successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '401': {
            'description': 'Authentication failed'
        }
    }
})
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    # Validate required fields
    if not current_password or not new_password:
        return jsonify(message="Missing required fields"), 400
    
    # Validate new password strength
    if not is_valid_password(new_password):
        return jsonify(message="New password must be at least 6 characters"), 400
    
    # Change password
    success, message = AuthService.change_password(user_id, current_password, new_password)
    if not success:
        return jsonify(message=message), 401
    
    return jsonify(message=message), 200
