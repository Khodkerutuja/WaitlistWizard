from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.mechanical_service import MechanicalServiceService
from services.wallet_service import WalletService
from schemas.mechanical_schema import mechanical_service_schema, mechanical_services_schema
from utils.auth_utils import active_user_required, provider_required
from models import ServiceStatus, BookingStatus
from flasgger import swag_from
from datetime import datetime

mechanical_bp = Blueprint('mechanical', __name__)

@mechanical_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Mechanical'],
    'summary': 'Get all mechanical services',
    'description': 'Get all available mechanical services',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by service type (repair, maintenance, etc.)'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of mechanical services'
        }
    }
})
def get_mechanical_services():
    service_type = request.args.get('type')
    
    if service_type:
        services = MechanicalServiceService.get_by_service_type(service_type)
    else:
        services = MechanicalServiceService.get_all()
    
    result = mechanical_services_schema.dump(services)
    return jsonify(services=result), 200

@mechanical_bp.route('/<int:service_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Mechanical'],
    'summary': 'Get mechanical service details',
    'description': 'Get mechanical service details by ID',
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
            'description': 'Mechanical service details'
        },
        '404': {
            'description': 'Service not found'
        }
    }
})
def get_mechanical_service(service_id):
    service = MechanicalServiceService.get_by_id(service_id)
    
    if not service:
        return jsonify(message="Service not found"), 404
    
    result = mechanical_service_schema.dump(service)
    return jsonify(service=result), 200

@mechanical_bp.route('/', methods=['POST'])
@jwt_required()
@provider_required()
@active_user_required()
@swag_from({
    'tags': ['Mechanical'],
    'summary': 'Create mechanical service',
    'description': 'Create a new mechanical service (provider only)',
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
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'price': {'type': 'number', 'minimum': 0},
                    'service_type': {'type': 'string'},
                    'vehicle_types': {'type': 'string'}
                },
                'required': ['name', 'price', 'service_type']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Mechanical service created successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Provider access required'
        }
    }
})
def create_mechanical_service():
    provider_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate required fields
    required_fields = ['name', 'price', 'service_type']
    for field in required_fields:
        if field not in data:
            return jsonify(message=f"Missing required field: {field}"), 400
    
    # Create service
    service, message = MechanicalServiceService.create_mechanical_service(provider_id, data)
    if not service:
        return jsonify(message=message), 400
    
    result = mechanical_service_schema.dump(service)
    return jsonify(message=message, service=result), 201

@mechanical_bp.route('/<int:service_id>/book', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Mechanical'],
    'summary': 'Book mechanical service',
    'description': 'Book a mechanical service',
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
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'booking_date': {'type': 'string', 'format': 'date-time'},
                    'notes': {'type': 'string'}
                },
                'required': ['booking_date']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Service booked successfully'
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
def book_mechanical_service(service_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    booking_date_str = data.get('booking_date')
    notes = data.get('notes')
    
    # Validate required fields
    if not booking_date_str:
        return jsonify(message="Missing required field: booking_date"), 400
    
    # Validate date format
    try:
        booking_date = datetime.fromisoformat(booking_date_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify(message="Invalid booking_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"), 400
    
    # Get service to check price
    service = MechanicalServiceService.get_by_id(service_id)
    if not service:
        return jsonify(message="Service not found"), 404
    
    # Check if service is available
    if service.status != ServiceStatus.AVAILABLE:
        return jsonify(message="Service is not available"), 400
    
    # Process payment
    amount = service.price
    payment_result, payment_message = WalletService.process_payment(
        user_id, 
        service.provider_id, 
        amount, 
        f"mechanical_booking_{service_id}_{user_id}",
        f"Booking for {service.name} ({service.service_type})"
    )
    
    if not payment_result:
        return jsonify(message=payment_message), 400
    
    # Book service
    booking, message = MechanicalServiceService.book_mechanical_service(user_id, service_id, booking_date, amount, notes)
    if not booking:
        # Refund payment if booking fails
        WalletService.refund_payment(
            user_id, 
            amount, 
            f"refund_mechanical_{service_id}_{user_id}",
            f"Refund for failed booking: {service.name}"
        )
        return jsonify(message=message), 400
    
    return jsonify(message=message, booking_id=booking.id), 201

@mechanical_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Mechanical'],
    'summary': 'Cancel booking',
    'description': 'Cancel a mechanical service booking',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'booking_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Booking ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Booking cancelled successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Not authorized'
        },
        '404': {
            'description': 'Booking not found'
        }
    }
})
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    
    # Cancel booking
    success, message = MechanicalServiceService.cancel_booking(user_id, booking_id)
    if not success:
        if "not authorized" in message.lower():
            return jsonify(message=message), 403
        elif "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    # Get booking to process refund
    from models import Booking
    booking = Booking.query.get(booking_id)
    
    # Process refund
    refund_result, refund_message = WalletService.refund_payment(
        user_id, 
        booking.amount, 
        f"refund_mechanical_{booking.service_id}_{user_id}",
        f"Refund for cancelled booking #{booking_id}"
    )
    
    if not refund_result:
        return jsonify(message=f"Booking cancelled but refund failed: {refund_message}"), 200
    
    return jsonify(message=f"{message}. {refund_message}"), 200

@mechanical_bp.route('/provider/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
@provider_required()
@active_user_required()
@swag_from({
    'tags': ['Mechanical'],
    'summary': 'Update booking status',
    'description': 'Update a mechanical service booking status (provider only)',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'booking_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Booking ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['confirmed', 'rejected', 'completed']}
                },
                'required': ['status']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Booking status updated successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Not authorized'
        },
        '404': {
            'description': 'Booking not found'
        }
    }
})
def update_booking_status(booking_id):
    provider_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    status_str = data.get('status')
    
    # Validate required fields
    if not status_str:
        return jsonify(message="Missing required field: status"), 400
    
    # Validate status
    try:
        status = BookingStatus(status_str)
    except ValueError:
        return jsonify(message="Invalid status"), 400
    
    # Update booking status
    success, message = MechanicalServiceService.update_booking_status(provider_id, booking_id, status)
    if not success:
        if "not authorized" in message.lower():
            return jsonify(message=message), 403
        elif "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    # Process refund if booking is rejected
    if status == BookingStatus.REJECTED:
        from models import Booking
        booking = Booking.query.get(booking_id)
        
        if booking:
            # Process refund to consumer
            refund_result, refund_message = WalletService.refund_payment(
                booking.consumer_id, 
                booking.amount, 
                f"refund_reject_{booking.service_id}_{booking.consumer_id}",
                f"Refund for rejected booking #{booking_id}"
            )
            
            if not refund_result:
                return jsonify(message=f"Booking status updated but refund failed: {refund_message}"), 200
            
            message = f"{message}. {refund_message}"
    
    return jsonify(message=message), 200
