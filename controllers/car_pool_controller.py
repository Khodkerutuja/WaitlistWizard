from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.car_pool_service import CarPoolService
from utils.jwt_manager import service_provider_required
from models.car_pool import VehicleType

car_pool_bp = Blueprint('car_pool', __name__)
car_pool_service = CarPoolService()

@car_pool_bp.route('/', methods=['GET'])
@jwt_required()
def get_car_pool_services():
    """
    Get all car/bike pool services
    ---
    tags:
      - Car Pool
    security:
      - JWT: []
    parameters:
      - name: vehicle_type
        in: query
        type: string
        required: false
        enum: [CAR, BIKE]
        description: Filter by vehicle type
      - name: source
        in: query
        type: string
        required: false
        description: Filter by source location
      - name: destination
        in: query
        type: string
        required: false
        description: Filter by destination
      - name: date
        in: query
        type: string
        required: false
        description: Filter by departure date (YYYY-MM-DD)
    responses:
      200:
        description: List of car/bike pool services
      401:
        description: Unauthorized
    """
    vehicle_type = request.args.get('vehicle_type')
    source = request.args.get('source')
    destination = request.args.get('destination')
    date = request.args.get('date')
    
    try:
        services = car_pool_service.get_car_pool_services(
            vehicle_type=vehicle_type,
            source=source,
            destination=destination,
            date=date
        )
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@car_pool_bp.route('/', methods=['POST'])
@jwt_required()
@service_provider_required
def create_car_pool_service():
    """
    Create a new car/bike pool service
    ---
    tags:
      - Car Pool
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
            - vehicle_type
            - price
            - source
            - destination
            - departure_time
            - total_seats
          properties:
            name:
              type: string
            description:
              type: string
            vehicle_type:
              type: string
              enum: [CAR, BIKE]
            price:
              type: number
            source:
              type: string
            destination:
              type: string
            departure_time:
              type: string
              format: date-time
            total_seats:
              type: integer
            vehicle_model:
              type: string
            vehicle_number:
              type: string
    responses:
      201:
        description: Car/bike pool service created successfully
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
    required_fields = ['name', 'description', 'vehicle_type', 'price', 'source', 
                      'destination', 'departure_time', 'total_seats']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate vehicle type
    vehicle_type = data['vehicle_type']
    if vehicle_type not in [VehicleType.CAR, VehicleType.BIKE]:
        return jsonify({'error': 'Invalid vehicle type'}), 400
    
    try:
        service = car_pool_service.create_car_pool_service(
            name=data['name'],
            description=data['description'],
            provider_id=provider_id,
            vehicle_type=vehicle_type,
            price=float(data['price']),
            source=data['source'],
            destination=data['destination'],
            departure_time=data['departure_time'],
            total_seats=int(data['total_seats']),
            vehicle_model=data.get('vehicle_model'),
            vehicle_number=data.get('vehicle_number')
        )
        
        return jsonify({'message': 'Car/bike pool service created successfully', 'service': service.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@car_pool_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@service_provider_required
def update_car_pool_service(service_id):
    """
    Update a car/bike pool service
    ---
    tags:
      - Car Pool
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
            source:
              type: string
            destination:
              type: string
            departure_time:
              type: string
              format: date-time
            vehicle_model:
              type: string
            vehicle_number:
              type: string
    responses:
      200:
        description: Car/bike pool service updated successfully
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
        service = car_pool_service.update_car_pool_service(
            service_id=service_id,
            provider_id=provider_id,
            data=data
        )
        
        return jsonify({'message': 'Car/bike pool service updated successfully', 'service': service.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@car_pool_bp.route('/<int:service_id>/book', methods=['POST'])
@jwt_required()
def book_car_pool_service(service_id):
    """
    Book a car/bike pool service
    ---
    tags:
      - Car Pool
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
            - num_seats
          properties:
            num_seats:
              type: integer
              minimum: 1
    responses:
      200:
        description: Car/bike pool service booked successfully
      400:
        description: Invalid input data or insufficient seats
      401:
        description: Unauthorized
      404:
        description: Service not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    data = request.get_json()
    
    # Validate required fields
    if 'num_seats' not in data:
        return jsonify({'error': 'Number of seats is required'}), 400
    
    try:
        num_seats = int(data['num_seats'])
        if num_seats <= 0:
            return jsonify({'error': 'Number of seats must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid number of seats'}), 400
    
    try:
        booking = car_pool_service.book_car_pool_service(
            user_id=user_id,
            service_id=service_id,
            num_seats=num_seats
        )
        
        return jsonify({'message': 'Car/bike pool service booked successfully', 'booking': booking.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
