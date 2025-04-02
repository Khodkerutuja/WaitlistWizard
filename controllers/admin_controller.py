from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.admin_service import AdminService
from utils.jwt_manager import admin_required

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    """
    Get admin dashboard statistics
    ---
    tags:
      - Admin
    security:
      - JWT: []
    responses:
      200:
        description: Admin dashboard statistics
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    try:
        stats = admin_service.get_dashboard_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services', methods=['GET'])
@jwt_required()
@admin_required
def get_all_services_admin():
    """
    Get all services (Admin view)
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Filter by service status
    responses:
      200:
        description: List of all services
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    status = request.args.get('status')
    
    try:
        services = admin_service.get_all_services(status)
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
@admin_required
def get_all_bookings_admin():
    """
    Get all bookings (Admin view)
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Filter by booking status
    responses:
      200:
        description: List of all bookings
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    status = request.args.get('status')
    
    try:
        bookings = admin_service.get_all_bookings(status)
        return jsonify([booking.to_dict() for booking in bookings]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/transactions', methods=['GET'])
@jwt_required()
@admin_required
def get_all_transactions_admin():
    """
    Get all wallet transactions (Admin view)
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: transaction_type
        in: query
        type: string
        required: false
        description: Filter by transaction type
      - name: limit
        in: query
        type: integer
        required: false
        default: 50
        description: Limit the number of results
    responses:
      200:
        description: List of all transactions
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    transaction_type = request.args.get('transaction_type')
    limit = request.args.get('limit', 50, type=int)
    
    try:
        transactions = admin_service.get_all_transactions(transaction_type, limit)
        return jsonify([transaction.to_dict() for transaction in transactions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/<int:service_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_service(service_id):
    """
    Update a service (Admin only)
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        description: Service ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [AVAILABLE, UNAVAILABLE, DELETED]
            # Other service fields can be updated by admin
    responses:
      200:
        description: Service updated successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Service not found
    """
    data = request.get_json()
    
    try:
        service = admin_service.update_service(service_id, data)
        return jsonify({'message': 'Service updated successfully', 'service': service.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_service(service_id):
    """
    Delete a service (Admin only)
    ---
    tags:
      - Admin
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
        description: Service deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Service not found
    """
    try:
        admin_service.delete_service(service_id)
        return jsonify({'message': 'Service deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_user(user_id):
    """
    Update a user's status (Admin only)
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [ACTIVE, INACTIVE]
    responses:
      200:
        description: User status updated successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: User not found
    """
    data = request.get_json()
    
    # Validate required fields
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    try:
        user = admin_service.update_user_status(user_id, data['status'])
        return jsonify({'message': 'User status updated successfully', 'user': user.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
