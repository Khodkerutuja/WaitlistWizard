from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.service_service import ServiceService
from utils.jwt_manager import admin_required, service_provider_required
from models.service import ServiceType, ServiceStatus

service_bp = Blueprint('service', __name__)
service_service = ServiceService()

@service_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_services():
    """
    Get all services
    ---
    tags:
      - Services
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
        description: Filter by status (default is AVAILABLE)
      - name: provider_id
        in: query
        type: integer
        required: false
        description: Filter by provider ID
    responses:
      200:
        description: List of services
      401:
        description: Unauthorized
    """
    service_type = request.args.get('service_type')
    status = request.args.get('status', ServiceStatus.AVAILABLE)
    provider_id = request.args.get('provider_id', type=int)
    
    try:
        services = service_service.get_all_services(
            service_type=service_type,
            status=status,
            provider_id=provider_id
        )
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service(service_id):
    """
    Get a specific service
    ---
    tags:
      - Services
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
        description: Service details
      401:
        description: Unauthorized
      404:
        description: Service not found
    """
    try:
        service = service_service.get_service_by_id(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        return jsonify(service.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/', methods=['POST'])
@jwt_required()
@service_provider_required
def create_service():
    """
    Create a new service (Service Provider only)
    ---
    tags:
      - Services
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - description
            - service_type
            - price
          properties:
            name:
              type: string
            description:
              type: string
            service_type:
              type: string
              enum: [CAR_POOL, BIKE_POOL, GYM_FITNESS, HOUSEHOLD, MECHANICAL]
            price:
              type: number
            location:
              type: string
            availability:
              type: string
            # Additional fields based on service type would be included here
    responses:
      201:
        description: Service created successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Forbidden - Service Provider access required
    """
    identity = get_jwt_identity()
    provider_id = identity['user_id']
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'description', 'service_type', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate service type
    service_type = data['service_type']
    if service_type not in [ServiceType.CAR_POOL, ServiceType.BIKE_POOL, 
                          ServiceType.GYM_FITNESS, ServiceType.HOUSEHOLD, 
                          ServiceType.MECHANICAL]:
        return jsonify({'error': 'Invalid service type'}), 400
    
    try:
        service = service_service.create_service(
            name=data['name'],
            description=data['description'],
            provider_id=provider_id,
            service_type=service_type,
            price=float(data['price']),
            location=data.get('location'),
            availability=data.get('availability'),
            additional_data=data  # Pass all data for service-specific fields
        )
        
        return jsonify({'message': 'Service created successfully', 'service': service.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    """
    Update a service (Service Provider who owns the service or Admin)
    ---
    tags:
      - Services
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
            name:
              type: string
            description:
              type: string
            price:
              type: number
            status:
              type: string
              enum: [AVAILABLE, UNAVAILABLE]
            location:
              type: string
            availability:
              type: string
            # Additional fields based on service type would be included here
    responses:
      200:
        description: Service updated successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not authorized to update this service
      404:
        description: Service not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    role = identity['role']
    data = request.get_json()
    
    try:
        # Check if user is authorized to update this service
        service = service_service.get_service_by_id(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        if service.provider_id != user_id and role != 'ADMIN':
            return jsonify({'error': 'Not authorized to update this service'}), 403
        
        updated_service = service_service.update_service(
            service_id=service_id,
            data=data
        )
        
        return jsonify({'message': 'Service updated successfully', 'service': updated_service.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    """
    Delete a service (Service Provider who owns the service or Admin)
    ---
    tags:
      - Services
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
        description: Forbidden - Not authorized to delete this service
      404:
        description: Service not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    role = identity['role']
    
    try:
        # Check if user is authorized to delete this service
        service = service_service.get_service_by_id(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        if service.provider_id != user_id and role != 'ADMIN':
            return jsonify({'error': 'Not authorized to delete this service'}), 403
        
        service_service.delete_service(service_id)
        
        return jsonify({'message': 'Service deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/<int:service_id>/book', methods=['POST'])
@jwt_required()
def book_service(service_id):
    """
    Book a service
    ---
    tags:
      - Services
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
          required:
            - booking_time
          properties:
            booking_time:
              type: string
              format: date-time
            # Additional fields based on service type would be included here
    responses:
      200:
        description: Service booked successfully
      400:
        description: Invalid input data or insufficient wallet balance
      401:
        description: Unauthorized
      404:
        description: Service not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    data = request.get_json()
    
    # Validate required fields
    if 'booking_time' not in data:
        return jsonify({'error': 'Booking time is required'}), 400
    
    try:
        booking = service_service.book_service(
            user_id=user_id,
            service_id=service_id,
            booking_time=data['booking_time'],
            additional_data=data
        )
        
        return jsonify({'message': 'Service booked successfully', 'booking': booking.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    """
    Get current user's bookings
    ---
    tags:
      - Services
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
        description: List of bookings
      401:
        description: Unauthorized
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    status = request.args.get('status')
    
    try:
        bookings = service_service.get_user_bookings(user_id, status)
        return jsonify([booking.to_dict() for booking in bookings]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/provider/bookings', methods=['GET'])
@jwt_required()
@service_provider_required
def get_provider_bookings():
    """
    Get service provider's bookings
    ---
    tags:
      - Services
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
        description: List of bookings
      401:
        description: Unauthorized
      403:
        description: Forbidden - Service Provider access required
    """
    identity = get_jwt_identity()
    provider_id = identity['user_id']
    status = request.args.get('status')
    
    try:
        bookings = service_service.get_provider_bookings(provider_id, status)
        return jsonify([booking.to_dict() for booking in bookings]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    """
    Cancel a booking
    ---
    tags:
      - Services
    security:
      - JWT: []
    parameters:
      - name: booking_id
        in: path
        type: integer
        required: true
        description: Booking ID
    responses:
      200:
        description: Booking cancelled successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not authorized to cancel this booking
      404:
        description: Booking not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    try:
        booking = service_service.cancel_booking(booking_id, user_id)
        return jsonify({'message': 'Booking cancelled successfully', 'booking': booking.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/provider/bookings/<int:booking_id>/update', methods=['POST'])
@jwt_required()
@service_provider_required
def update_booking_status(booking_id):
    """
    Update booking status (Service Provider only)
    ---
    tags:
      - Services
    security:
      - JWT: []
    parameters:
      - name: booking_id
        in: path
        type: integer
        required: true
        description: Booking ID
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
              enum: [CONFIRMED, REJECTED, COMPLETED]
    responses:
      200:
        description: Booking status updated successfully
      400:
        description: Invalid status
      401:
        description: Unauthorized
      403:
        description: Forbidden - Service Provider access required or not your booking
      404:
        description: Booking not found
    """
    identity = get_jwt_identity()
    provider_id = identity['user_id']
    data = request.get_json()
    
    # Validate required fields
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    try:
        booking = service_service.update_booking_status(booking_id, provider_id, data['status'])
        return jsonify({'message': 'Booking status updated successfully', 'booking': booking.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
