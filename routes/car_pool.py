from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.car_pool_service import CarPoolServiceService
from services.wallet_service import WalletService
from schemas.car_pool_schema import car_pool_service_schema, car_pool_services_schema
from utils.auth_utils import active_user_required, provider_required
from models import ServiceStatus, BookingStatus
from utils.validation import is_valid_date_format
from flasgger import swag_from
from datetime import datetime

car_pool_bp = Blueprint('car_pool', __name__)

@car_pool_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Car Pool'],
    'summary': 'Get all car pool services',
    'description': 'Get all available car/bike pool services',
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
            'description': 'List of car pool services'
        }
    }
})
def get_car_pool_services():
    services = CarPoolServiceService.get_all()
    result = car_pool_services_schema.dump(services)
    return jsonify(services=result), 200

@car_pool_bp.route('/search', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Car Pool'],
    'summary': 'Search rides',
    'description': 'Search for available rides by source, destination, and date',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'source',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Source location'
        },
        {
            'name': 'destination',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Destination location'
        },
        {
            'name': 'date',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Departure date (YYYY-MM-DD)'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of available rides'
        },
        '400': {
            'description': 'Invalid input data'
        }
    }
})
def search_rides():
    source = request.args.get('source')
    destination = request.args.get('destination')
    date = request.args.get('date')
    
    # Validate input
    if not source or not destination or not date:
        return jsonify(message="Missing required parameters"), 400
    
    # Validate date format
    if not is_valid_date_format(date, '%Y-%m-%d'):
        return jsonify(message="Invalid date format. Use YYYY-MM-DD"), 400
    
    # Search rides
    rides = CarPoolServiceService.search_rides(source, destination, date)
    
    result = car_pool_services_schema.dump(rides)
    return jsonify(rides=result), 200

@car_pool_bp.route('/', methods=['POST'])
@jwt_required()
@provider_required()
@active_user_required()
@swag_from({
    'tags': ['Car Pool'],
    'summary': 'Create car pool service',
    'description': 'Create a new car/bike pool service (provider only)',
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
                    'vehicle_type': {'type': 'string', 'enum': ['car', 'bike']},
                    'vehicle_model': {'type': 'string'},
                    'capacity': {'type': 'integer', 'minimum': 1},
                    'available_seats': {'type': 'integer', 'minimum': 0},
                    'source': {'type': 'string'},
                    'destination': {'type': 'string'},
                    'departure_time': {'type': 'string', 'format': 'date-time'}
                },
                'required': ['name', 'price', 'vehicle_type', 'capacity', 'available_seats', 'source', 'destination', 'departure_time']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Car pool service created successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Provider access required'
        }
    }
})
def create_car_pool_service():
    provider_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate required fields
    required_fields = ['name', 'price', 'vehicle_type', 'capacity', 'available_seats', 'source', 'destination', 'departure_time']
    for field in required_fields:
        if field not in data:
            return jsonify(message=f"Missing required field: {field}"), 400
    
    # Validate date format
    try:
        departure_time = datetime.fromisoformat(data['departure_time'].replace('Z', '+00:00'))
        data['departure_time'] = departure_time
    except ValueError:
        return jsonify(message="Invalid departure_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"), 400
    
    # Create service
    service, message = CarPoolServiceService.create_car_pool_service(provider_id, data)
    if not service:
        return jsonify(message=message), 400
    
    result = car_pool_service_schema.dump(service)
    return jsonify(message=message, service=result), 201

@car_pool_bp.route('/<int:service_id>/book', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Car Pool'],
    'summary': 'Book a ride',
    'description': 'Book a car/bike pool ride',
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
            'description': 'Ride booked successfully'
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
def book_ride(service_id):
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
    service = CarPoolServiceService.get_by_id(service_id)
    if not service:
        return jsonify(message="Service not found"), 404
    
    # Check if service is available
    if service.status != ServiceStatus.AVAILABLE:
        return jsonify(message="Service is not available"), 400
    
    # Check if there are available seats
    if service.available_seats <= 0:
        return jsonify(message="No available seats"), 400
    
    # Process payment
    amount = service.price
    payment_result, payment_message = WalletService.process_payment(
        user_id, 
        service.provider_id, 
        amount, 
        f"car_pool_booking_{service_id}_{user_id}",
        f"Booking for {service.name} from {service.source} to {service.destination}"
    )
    
    if not payment_result:
        return jsonify(message=payment_message), 400
    
    # Book ride
    booking, message = CarPoolServiceService.book_ride(user_id, service_id, booking_date, amount, notes)
    if not booking:
        # Refund payment if booking fails
        WalletService.refund_payment(
            user_id, 
            amount, 
            f"refund_car_pool_{service_id}_{user_id}",
            f"Refund for failed booking: {service.name}"
        )
        return jsonify(message=message), 400
    
    return jsonify(message=message, booking_id=booking.id), 201

@car_pool_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Car Pool'],
    'summary': 'Cancel booking',
    'description': 'Cancel a car/bike pool booking',
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
    success, message = CarPoolServiceService.cancel_booking(user_id, booking_id)
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
        f"refund_car_pool_{booking.service_id}_{user_id}",
        f"Refund for cancelled booking #{booking_id}"
    )
    
    if not refund_result:
        return jsonify(message=f"Booking cancelled but refund failed: {refund_message}"), 200
    
    return jsonify(message=f"{message}. {refund_message}"), 200
