from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.mechanical_service import MechanicalService
from utils.jwt_manager import service_provider_required
from models.mechanical import MechanicalServiceType

mechanical_bp = Blueprint('mechanical', __name__)
mechanical_service = MechanicalService()

@mechanical_bp.route('/', methods=['GET'])
@jwt_required()
def get_mechanical_services():
    """
    Get all mechanical services
    ---
    tags:
      - Mechanical
    security:
      - JWT: []
    parameters:
      - name: mechanical_type
        in: query
        type: string
        required: false
        description: Filter by mechanical service type (e.g., BIKE_REPAIR, CAR_REPAIR)
      - name: offers_pickup
        in: query
        type: boolean
        required: false
        description: Filter by pickup service availability
      - name: location
        in: query
        type: string
        required: false
        description: Filter by location
    responses:
      200:
        description: List of mechanical services
      401:
        description: Unauthorized
    """
    mechanical_type = request.args.get('mechanical_type')
    offers_pickup = request.args.get('offers_pickup', type=bool)
    location = request.args.get('location')
    
    try:
        services = mechanical_service.get_mechanical_services(
            mechanical_type=mechanical_type,
            offers_pickup=offers_pickup,
            location=location
        )
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mechanical_bp.route('/', methods=['POST'])
@jwt_required()
@service_provider_required
def create_mechanical_service():
    """
    Create a new mechanical service
    ---
    tags:
      - Mechanical
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
            - mechanical_type
            - service_charge
          properties:
            name:
              type: string
            description:
              type: string
            mechanical_type:
              type: string
              enum: [BIKE_REPAIR, CAR_REPAIR, GENERAL_MAINTENANCE, BREAKDOWN_ASSISTANCE, TOWING, OTHER]
            service_charge:
              type: number
            additional_charges_desc:
              type: string
            estimated_time:
              type: integer
            offers_pickup:
              type: boolean
            pickup_charge:
              type: number
            location:
              type: string
            availability:
              type: string
    responses:
      201:
        description: Mechanical service created successfully
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
    required_fields = ['name', 'description', 'mechanical_type', 'service_charge']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate mechanical type
    mechanical_type = data['mechanical_type']
    if mechanical_type not in [MechanicalServiceType.BIKE_REPAIR, MechanicalServiceType.CAR_REPAIR, 
                              MechanicalServiceType.GENERAL_MAINTENANCE, MechanicalServiceType.BREAKDOWN_ASSISTANCE, 
                              MechanicalServiceType.TOWING, MechanicalServiceType.OTHER]:
        return jsonify({'error': 'Invalid mechanical service type'}), 400
    
    try:
        service = mechanical_service.create_mechanical_service(
            name=data['name'],
            description=data['description'],
            provider_id=provider_id,
            mechanical_type=mechanical_type,
            service_charge=float(data['service_charge']),
            additional_charges_desc=data.get('additional_charges_desc'),
            estimated_time=data.get('estimated_time'),
            offers_pickup=data.get('offers_pickup', False),
            pickup_charge=data.get('pickup_charge'),
            location=data.get('location'),
            availability=data.get('availability')
        )
        
        return jsonify({'message': 'Mechanical service created successfully', 'service': service.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mechanical_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@service_provider_required
def update_mechanical_service(service_id):
    """
    Update a mechanical service
    ---
    tags:
      - Mechanical
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
            service_charge:
              type: number
            additional_charges_desc:
              type: string
            estimated_time:
              type: integer
            offers_pickup:
              type: boolean
            pickup_charge:
              type: number
            location:
              type: string
            availability:
              type: string
    responses:
      200:
        description: Mechanical service updated successfully
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
        service = mechanical_service.update_mechanical_service(
            service_id=service_id,
            provider_id=provider_id,
            data=data
        )
        
        return jsonify({'message': 'Mechanical service updated successfully', 'service': service.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mechanical_bp.route('/<int:service_id>/book', methods=['POST'])
@jwt_required()
def book_mechanical_service(service_id):
    """
    Book a mechanical service
    ---
    tags:
      - Mechanical
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
            vehicle_details:
              type: string
            issue_description:
              type: string
            pickup_required:
              type: boolean
            pickup_address:
              type: string
    responses:
      200:
        description: Mechanical service booked successfully
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
        booking = mechanical_service.book_mechanical_service(
            user_id=user_id,
            service_id=service_id,
            booking_time=data['booking_time'],
            vehicle_details=data.get('vehicle_details'),
            issue_description=data.get('issue_description'),
            pickup_required=data.get('pickup_required', False),
            pickup_address=data.get('pickup_address')
        )
        
        return jsonify({'message': 'Mechanical service booked successfully', 'booking': booking.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
