from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_service import UserService
from utils.jwt_manager import admin_required, service_provider_required

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """
    Get all users (Admin only)
    ---
    tags:
      - Users
    security:
      - JWT: []
    parameters:
      - name: role
        in: query
        type: string
        required: false
        description: Filter by user role (USER, POWER_USER, ADMIN)
      - name: status
        in: query
        type: string
        required: false
        description: Filter by user status (ACTIVE, PENDING, INACTIVE)
    responses:
      200:
        description: List of users
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    role = request.args.get('role')
    status = request.args.get('status')
    
    try:
        users = user_service.get_all_users(role=role, status=status)
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get a specific user
    ---
    tags:
      - Users
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User details
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not authorized to view this user
      404:
        description: User not found
    """
    identity = get_jwt_identity()
    current_user_id = identity['user_id']
    role = identity['role']
    
    # Only allow admin to view other users or users to view their own profile
    if current_user_id != user_id and role != 'ADMIN':
        return jsonify({'error': 'Not authorized to view this user'}), 403
    
    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/providers', methods=['GET'])
@jwt_required()
def get_service_providers():
    """
    Get all service providers
    ---
    tags:
      - Users
    security:
      - JWT: []
    parameters:
      - name: service_type
        in: query
        type: string
        required: false
        description: Filter by service type
      - name: status
        in: query
        type: string
        required: false
        description: Filter by status (default is ACTIVE)
    responses:
      200:
        description: List of service providers
      401:
        description: Unauthorized
    """
    service_type = request.args.get('service_type')
    status = request.args.get('status', 'ACTIVE')
    
    try:
        providers = user_service.get_service_providers(service_type=service_type, status=status)
        return jsonify([provider.to_dict() for provider in providers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/providers/pending', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_providers():
    """
    Get all pending service providers (Admin only)
    ---
    tags:
      - Users
    security:
      - JWT: []
    responses:
      200:
        description: List of pending service providers
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    try:
        providers = user_service.get_service_providers(status='PENDING')
        return jsonify([provider.to_dict() for provider in providers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/providers/<int:provider_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_provider(provider_id):
    """
    Approve a service provider (Admin only)
    ---
    tags:
      - Users
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
        description: Provider approved successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Provider not found
    """
    try:
        provider = user_service.approve_service_provider(provider_id)
        return jsonify({'message': 'Service provider approved successfully', 'provider': provider.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/providers/<int:provider_id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required
def deactivate_provider(provider_id):
    """
    Deactivate a service provider (Admin only)
    ---
    tags:
      - Users
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
        description: Provider deactivated successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Provider not found
    """
    try:
        provider = user_service.deactivate_service_provider(provider_id)
        return jsonify({'message': 'Service provider deactivated successfully', 'provider': provider.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
