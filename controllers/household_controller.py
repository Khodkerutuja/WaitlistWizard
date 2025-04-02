from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.household_service import HouseholdService
from utils.jwt_manager import service_provider_required
from models.household import HouseholdServiceType

household_bp = Blueprint('household', __name__)
household_service = HouseholdService()

@household_bp.route('/', methods=['GET'])
@jwt_required()
def get_household_services():
    """
    Get all household services
    ---
    tags:
      - Household
    security:
      - JWT: []
    parameters:
      - name: household_type
        in: query
        type: string
        required: false
        description: Filter by household service type (e.g., MAID, PLUMBING)
      - name: location
        in: query
        type: string
        required: false
        description: Filter by location
    responses:
      200:
        description: List of household services
      401:
        description: Unauthorized
    """
    household_type = request.args.get('household_type')
    location = request.args.get('location')
    
    try:
        services = household_service.get_household_services(
            household_type=household_type,
            location=location
        )
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@household_bp.route('/', methods=['POST'])
@jwt_required()
@service_provider_required
def create_household_service():
    """
    Create a new household service
    ---
    tags:
      - Household
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
            - household_type
            - price
          properties:
            name:
              type: string
            description:
              type: string
            household_type:
              type: string
              enum: [MAID, PLUMBING, ELECTRICAL, PEST_CONTROL, CLEANING, OTHER]
            price:
              type: number
            hourly_rate:
              type: number
            visit_charge:
              type: number
            estimated_duration:
              type: integer
            location:
              type: string
            availability:
              type: string
    responses:
      201:
        description: Household service created successfully
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
    required_fields = ['name', 'description', 'household_type', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate household type
    household_type = data['household_type']
    if household_type not in [HouseholdServiceType.MAID, HouseholdServiceType.PLUMBING, 
                             HouseholdServiceType.ELECTRICAL, HouseholdServiceType.PEST_CONTROL, 
                             HouseholdServiceType.CLEANING, HouseholdServiceType.OTHER]:
        return jsonify({'error': 'Invalid household service type'}), 400
    
    try:
        service = household_service.create_household_service(
            name=data['name'],
            description=data['description'],
            provider_id=provider_id,
            household_type=household_type,
            price=float(data['price']),
            hourly_rate=data.get('hourly_rate'),
            visit_charge=data.get('visit_charge'),
            estimated_duration=data.get('estimated_duration'),
            location=data.get('location'),
            availability=data.get('availability')
        )
        
        return jsonify({'message': 'Household service created successfully', 'service': service.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@household_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@service_provider_required
def update_household_service(service_id):
    """
    Update a household service
    ---
    tags:
      - Household
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
            hourly_rate:
              type: number
            visit_charge:
              type: number
            estimated_duration:
              type: integer
            location:
              type: string
            availability:
              type: string
    responses:
      200:
        description: Household service updated successfully
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
    provider_id = identity['user_id']
    data = request.get_json()
    
    try:
        service = household_service.update_household_service(
            service_id=service_id,
            provider_id=provider_id,
            data=data
        )
        
        return jsonify({'message': 'Household service updated successfully', 'service': service.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@household_bp.route('/<int:service_id>/book', methods=['POST'])
@jwt_required()
def book_household_service(service_id):
    """
    Book a household service
    ---
    tags:
      - Household
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
            hours:
              type: number
              description: Required for hourly rate services
            address:
              type: string
              description: Service delivery address
    responses:
      200:
        description: Household service booked successfully
      400:
        description: Invalid input data
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
        booking = household_service.book_household_service(
            user_id=user_id,
            service_id=service_id,
            booking_time=data['booking_time'],
            hours=data.get('hours'),
            address=data.get('address')
        )
        
        return jsonify({'message': 'Household service booked successfully', 'booking': booking.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
