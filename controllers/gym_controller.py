from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.gym_service import GymService
from utils.jwt_manager import service_provider_required
from models.gym import SubscriptionPlan

gym_bp = Blueprint('gym', __name__)
gym_service = GymService()

@gym_bp.route('/', methods=['GET'])
@jwt_required()
def get_gym_services():
    """
    Get all gym services
    ---
    tags:
      - Gym
    security:
      - JWT: []
    parameters:
      - name: facility_type
        in: query
        type: string
        required: false
        description: Filter by facility type (e.g., yoga, weightlifting)
      - name: trainers_available
        in: query
        type: boolean
        required: false
        description: Filter by trainer availability
      - name: dietician_available
        in: query
        type: boolean
        required: false
        description: Filter by dietician availability
    responses:
      200:
        description: List of gym services
      401:
        description: Unauthorized
    """
    facility_type = request.args.get('facility_type')
    trainers_available = request.args.get('trainers_available', type=bool)
    dietician_available = request.args.get('dietician_available', type=bool)
    
    try:
        services = gym_service.get_gym_services(
            facility_type=facility_type,
            trainers_available=trainers_available,
            dietician_available=dietician_available
        )
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gym_bp.route('/', methods=['POST'])
@jwt_required()
@service_provider_required
def create_gym_service():
    """
    Create a new gym service
    ---
    tags:
      - Gym
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
            - gym_name
            - facility_types
            - operating_hours
            - subscription_plans
          properties:
            name:
              type: string
            description:
              type: string
            gym_name:
              type: string
            facility_types:
              type: array
              items:
                type: string
            operating_hours:
              type: object
              properties:
                monday:
                  type: string
                tuesday:
                  type: string
                # ... other days
            subscription_plans:
              type: object
              properties:
                MONTHLY:
                  type: number
                QUARTERLY:
                  type: number
                ANNUAL:
                  type: number
            trainers_available:
              type: boolean
            dietician_available:
              type: boolean
            location:
              type: string
    responses:
      201:
        description: Gym service created successfully
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
    required_fields = ['name', 'description', 'gym_name', 'facility_types', 
                      'operating_hours', 'subscription_plans']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate subscription plans
    subscription_plans = data['subscription_plans']
    if not isinstance(subscription_plans, dict):
        return jsonify({'error': 'Subscription plans must be an object'}), 400
    
    for plan in [SubscriptionPlan.MONTHLY, SubscriptionPlan.QUARTERLY, SubscriptionPlan.ANNUAL]:
        if plan not in subscription_plans:
            return jsonify({'error': f'Subscription plan {plan} is required'}), 400
    
    try:
        service = gym_service.create_gym_service(
            name=data['name'],
            description=data['description'],
            provider_id=provider_id,
            gym_name=data['gym_name'],
            facility_types=data['facility_types'],
            operating_hours=data['operating_hours'],
            subscription_plans=data['subscription_plans'],
            trainers_available=data.get('trainers_available', False),
            dietician_available=data.get('dietician_available', False),
            location=data.get('location')
        )
        
        return jsonify({'message': 'Gym service created successfully', 'service': service.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gym_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@service_provider_required
def update_gym_service(service_id):
    """
    Update a gym service
    ---
    tags:
      - Gym
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
            gym_name:
              type: string
            facility_types:
              type: array
              items:
                type: string
            operating_hours:
              type: object
            subscription_plans:
              type: object
            trainers_available:
              type: boolean
            dietician_available:
              type: boolean
            location:
              type: string
    responses:
      200:
        description: Gym service updated successfully
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
        service = gym_service.update_gym_service(
            service_id=service_id,
            provider_id=provider_id,
            data=data
        )
        
        return jsonify({'message': 'Gym service updated successfully', 'service': service.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gym_bp.route('/<int:service_id>/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_gym(service_id):
    """
    Subscribe to a gym service
    ---
    tags:
      - Gym
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
            - subscription_plan
          properties:
            subscription_plan:
              type: string
              enum: [MONTHLY, QUARTERLY, ANNUAL]
            trainer_required:
              type: boolean
            dietician_required:
              type: boolean
    responses:
      200:
        description: Subscribed to gym service successfully
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
    if 'subscription_plan' not in data:
        return jsonify({'error': 'Subscription plan is required'}), 400
    
    # Validate subscription plan
    subscription_plan = data['subscription_plan']
    if subscription_plan not in [SubscriptionPlan.MONTHLY, SubscriptionPlan.QUARTERLY, SubscriptionPlan.ANNUAL]:
        return jsonify({'error': 'Invalid subscription plan'}), 400
    
    try:
        subscription = gym_service.subscribe_to_gym(
            user_id=user_id,
            service_id=service_id,
            subscription_plan=subscription_plan,
            trainer_required=data.get('trainer_required', False),
            dietician_required=data.get('dietician_required', False)
        )
        
        return jsonify({'message': 'Subscribed to gym service successfully', 'subscription': subscription.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gym_bp.route('/subscriptions', methods=['GET'])
@jwt_required()
def get_user_subscriptions():
    """
    Get current user's gym subscriptions
    ---
    tags:
      - Gym
    security:
      - JWT: []
    parameters:
      - name: active_only
        in: query
        type: boolean
        required: false
        default: true
        description: Filter by active subscriptions only
    responses:
      200:
        description: List of gym subscriptions
      401:
        description: Unauthorized
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    active_only = request.args.get('active_only', True, type=bool)
    
    try:
        subscriptions = gym_service.get_user_subscriptions(user_id, active_only)
        return jsonify([subscription.to_dict() for subscription in subscriptions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gym_bp.route('/provider/subscriptions', methods=['GET'])
@jwt_required()
@service_provider_required
def get_provider_subscriptions():
    """
    Get service provider's gym subscriptions
    ---
    tags:
      - Gym
    security:
      - JWT: []
    parameters:
      - name: active_only
        in: query
        type: boolean
        required: false
        default: true
        description: Filter by active subscriptions only
    responses:
      200:
        description: List of gym subscriptions
      401:
        description: Unauthorized
      403:
        description: Forbidden - Service Provider access required
    """
    identity = get_jwt_identity()
    provider_id = identity['user_id']
    active_only = request.args.get('active_only', True, type=bool)
    
    try:
        subscriptions = gym_service.get_provider_subscriptions(provider_id, active_only)
        return jsonify([subscription.to_dict() for subscription in subscriptions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
