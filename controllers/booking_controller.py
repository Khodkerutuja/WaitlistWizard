from flask import Blueprint, request, jsonify
from flask_login import current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from services.booking_service import BookingService
from services.service_service import ServiceService
from models.booking import BookingStatus
from utils.auth_utils import admin_required, service_provider_required

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/', methods=['GET'])
@jwt_required()
def get_bookings():
    """
    Get bookings for the current user or provider
    ---
    tags:
      - Bookings
    security:
      - JWT: []
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Filter by status
    responses:
      200:
        description: List of bookings
      401:
        description: Unauthorized
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    status = request.args.get('status')

    # Get all bookings for admin
    if current_user.is_admin:
        bookings = BookingService.get_all_bookings(status)
        return jsonify([booking.to_dict() for booking in bookings]), 200
    
    # Get bookings - different endpoints for consumer vs provider
    if current_user.is_service_provider:
        bookings = BookingService.get_provider_bookings(user_id, status)
    else:
        bookings = BookingService.get_user_bookings(user_id, status)
    
    return jsonify([booking.to_dict() for booking in bookings]), 200

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """
    Get booking details
    ---
    tags:
      - Bookings
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
        description: Booking details
      401:
        description: Unauthorized
      403:
        description: Forbidden
      404:
        description: Booking not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get the booking
    booking = BookingService.get_booking(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    # Check if the user has access to this booking
    # Admin can access all, provider checks service ownership, user checks booking ownership
    if not current_user.is_admin:
        if current_user.is_service_provider:
            service = ServiceService.get_service(booking.service_id)
            if not service or service.provider_id != user_id:
                return jsonify({"error": "You don't have access to this booking"}), 403
        elif booking.user_id != user_id:
            return jsonify({"error": "You don't have access to this booking"}), 403
    
    return jsonify(booking.to_dict()), 200

@booking_bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Create a new booking
    ---
    tags:
      - Bookings
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
          properties:
            service_id:
              type: integer
            quantity:
              type: integer
              default: 1
            notes:
              type: string
            start_time:
              type: string
              format: date-time
            end_time:
              type: string
              format: date-time
    responses:
      201:
        description: Booking created successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Cannot book your own service
      404:
        description: Service not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    if not data or 'service_id' not in data:
        return jsonify({"error": "service_id is required"}), 400
    
    service_id = data.get('service_id')
    
    # Check if the service exists
    service = ServiceService.get_service(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404
    
    # Check if the user is trying to book their own service
    if service.provider_id == user_id:
        return jsonify({"error": "You cannot book your own service"}), 403
    
    # Extract optional parameters
    quantity = data.get('quantity', 1)
    notes = data.get('notes')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    try:
        # Create the booking
        booking = BookingService.create_booking(
            service_id=service_id,
            user_id=user_id,
            quantity=quantity,
            notes=notes,
            start_time=start_time,
            end_time=end_time
        )
        
        return jsonify(booking.to_dict()), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error creating booking: {str(e)}"}), 500

@booking_bp.route('/<int:booking_id>/payment', methods=['POST'])
@jwt_required()
def process_payment(booking_id):
    """
    Process payment for a booking
    ---
    tags:
      - Bookings
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
        description: Payment processed successfully
      400:
        description: Invalid input data or insufficient funds
      401:
        description: Unauthorized
      403:
        description: Not your booking
      404:
        description: Booking not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get the booking
    booking = BookingService.get_booking(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    # Check if it's the user's booking
    if booking.user_id != user_id:
        return jsonify({"error": "Not your booking"}), 403
    
    # Check if the booking is in pending state
    if booking.status != BookingStatus.PENDING:
        return jsonify({"error": f"Booking is already {booking.status}"}), 400
    
    # Process payment
    success, message = BookingService.process_payment(booking_id)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    """
    Cancel a booking
    ---
    tags:
      - Bookings
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
      400:
        description: Cannot cancel booking in current state
      401:
        description: Unauthorized
      403:
        description: Not your booking
      404:
        description: Booking not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get the booking
    booking = BookingService.get_booking(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    # Check if the user has access to this booking (consumer or provider can cancel)
    service = ServiceService.get_service(booking.service_id)
    
    if not current_user.is_admin:
        if service.provider_id != user_id and booking.user_id != user_id:
            return jsonify({"error": "Not your booking"}), 403
    
    # Cancel the booking
    success, message = BookingService.cancel_booking(booking_id)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@booking_bp.route('/<int:booking_id>/complete', methods=['POST'])
@jwt_required()
def complete_booking(booking_id):
    """
    Mark a booking as completed (provider only)
    ---
    tags:
      - Bookings
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
        description: Booking marked as completed
      400:
        description: Cannot complete booking in current state
      401:
        description: Unauthorized
      403:
        description: Not your service
      404:
        description: Booking not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get the booking
    booking = BookingService.get_booking(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    # Check if it's the provider's service
    service = ServiceService.get_service(booking.service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404
    
    if not current_user.is_admin and service.provider_id != user_id:
        return jsonify({"error": "Not your service"}), 403
    
    # Mark booking as completed
    success, message = BookingService.complete_booking(booking_id)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@booking_bp.route('/<int:booking_id>/reject', methods=['POST'])
@jwt_required()
@service_provider_required
def reject_booking(booking_id):
    """
    Reject a booking (provider only)
    ---
    tags:
      - Bookings
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
        required: false
        schema:
          type: object
          properties:
            reason:
              type: string
    responses:
      200:
        description: Booking rejected
      400:
        description: Cannot reject booking in current state
      401:
        description: Unauthorized
      403:
        description: Not your service
      404:
        description: Booking not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get the booking
    booking = BookingService.get_booking(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    # Check if it's the provider's service
    service = ServiceService.get_service(booking.service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404
    
    if not current_user.is_admin and service.provider_id != user_id:
        return jsonify({"error": "Not your service"}), 403
    
    # Get reason if provided
    data = request.get_json() or {}
    reason = data.get('reason')
    
    # Reject booking
    success, message = BookingService.reject_booking(booking_id, reason)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400