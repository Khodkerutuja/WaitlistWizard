from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services.auth_service import AuthService
from models.user import UserRole
from utils.validators import validate_email, validate_password
from utils.jwt_manager import admin_required, service_provider_required

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - first_name
            - last_name
            - phone_number
          properties:
            email:
              type: string
            password:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            phone_number:
              type: string
            address:
              type: string
            role:
              type: string
              enum: [USER, POWER_USER]
            service_type:
              type: string
            description:
              type: string
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid input data
      409:
        description: Email already exists
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'phone_number']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email format
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password strength
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 8 characters and contain letters, numbers, and special characters'}), 400
    
    # Set default role if not provided
    role = data.get('role', UserRole.USER)
    if role not in [UserRole.USER, UserRole.POWER_USER]:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Additional fields required for service providers
    if role == UserRole.POWER_USER:
        if 'service_type' not in data or not data['service_type']:
            return jsonify({'error': 'Service type is required for service providers'}), 400
    
    try:
        user = auth_service.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            address=data.get('address'),
            role=role,
            service_type=data.get('service_type'),
            description=data.get('description')
        )
        return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    
    # Validate required fields
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        user = auth_service.authenticate_user(data['email'], data['password'])
        if user:
            # Create access token
            access_token = create_access_token(identity={
                'user_id': user.id,
                'role': user.role,
                'status': user.status
            })
            return jsonify({
                'access_token': access_token,
                'user_id': user.id,
                'role': user.role,
                'status': user.status
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile
    ---
    tags:
      - Authentication
    security:
      - JWT: []
    responses:
      200:
        description: User profile
      401:
        description: Unauthorized
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    try:
        user = auth_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile
    ---
    tags:
      - Authentication
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            first_name:
              type: string
            last_name:
              type: string
            phone_number:
              type: string
            address:
              type: string
            description:
              type: string
    responses:
      200:
        description: Profile updated successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    data = request.get_json()
    
    try:
        user = auth_service.update_user_profile(
            user_id=user_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            description=data.get('description')
        )
        return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """
    Change current user password
    ---
    tags:
      - Authentication
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
            new_password:
              type: string
    responses:
      200:
        description: Password changed successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized or incorrect current password
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['current_password', 'new_password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate password strength
    if not validate_password(data['new_password']):
        return jsonify({'error': 'New password must be at least 8 characters and contain letters, numbers, and special characters'}), 400
    
    try:
        success = auth_service.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        if success:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': 'Incorrect current password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
