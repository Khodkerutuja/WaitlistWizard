from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.gym_service import GymServiceService
from services.wallet_service import WalletService
from schemas.gym_schema import gym_service_schema, gym_services_schema
from utils.auth_utils import active_user_required, provider_required
from models import ServiceStatus, SubscriptionType
from flasgger import swag_from
from datetime import datetime

gym_bp = Blueprint('gym', __name__)

@gym_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Gym'],
    'summary': 'Get all gym services',
    'description': 'Get all available gym fitness services',
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
            'description': 'Filter by service type (fitness, yoga, zumba, etc.)'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of gym services'
        }
    }
})
def get_gym_services():
    service_type = request.args.get('type')
    
    if service_type:
        services = GymServiceService.get_by_service_type(service_type)
    else:
        services = GymServiceService.get_all()
    
    result = gym_services_schema.dump(services)
    return jsonify(services=result), 200

@gym_bp.route('/<int:service_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Gym'],
    'summary': 'Get gym service details',
    'description': 'Get gym service details by ID',
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
            'description': 'Gym service details'
        },
        '404': {
            'description': 'Service not found'
        }
    }
})
def get_gym_service(service_id):
    service = GymServiceService.get_by_id(service_id)
    
    if not service:
        return jsonify(message="Service not found"), 404
    
    result = gym_service_schema.dump(service)
    return jsonify(service=result), 200

@gym_bp.route('/', methods=['POST'])
@jwt_required()
@provider_required()
@active_user_required()
@swag_from({
    'tags': ['Gym'],
    'summary': 'Create gym service',
    'description': 'Create a new gym fitness service (provider only)',
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
                    'gym_name': {'type': 'string'},
                    'service_type': {'type': 'string'},
                    'trainer_name': {'type': 'string'},
                    'monthly_price': {'type': 'number', 'minimum': 0},
                    'quarterly_price': {'type': 'number', 'minimum': 0},
                    'annual_price': {'type': 'number', 'minimum': 0}
                },
                'required': ['name', 'price', 'gym_name', 'service_type', 'monthly_price', 'quarterly_price', 'annual_price']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Gym service created successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Provider access required'
        }
    }
})
def create_gym_service():
    provider_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate required fields
    required_fields = ['name', 'price', 'gym_name', 'service_type', 'monthly_price', 'quarterly_price', 'annual_price']
    for field in required_fields:
        if field not in data:
            return jsonify(message=f"Missing required field: {field}"), 400
    
    # Create service
    service, message = GymServiceService.create_gym_service(provider_id, data)
    if not service:
        return jsonify(message=message), 400
    
    result = gym_service_schema.dump(service)
    return jsonify(message=message, service=result), 201

@gym_bp.route('/<int:service_id>/subscribe', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Gym'],
    'summary': 'Subscribe to gym service',
    'description': 'Subscribe to a gym fitness service',
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
                    'subscription_type': {'type': 'string', 'enum': ['monthly', 'quarterly', 'annually']},
                    'notes': {'type': 'string'}
                },
                'required': ['subscription_type']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Subscription successful'
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
def subscribe_to_gym(service_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    subscription_type_str = data.get('subscription_type')
    notes = data.get('notes')
    
    # Validate required fields
    if not subscription_type_str:
        return jsonify(message="Missing required field: subscription_type"), 400
    
    # Validate subscription type
    try:
        subscription_type = SubscriptionType(subscription_type_str)
    except ValueError:
        return jsonify(message="Invalid subscription type"), 400
    
    # Get service to check price
    service = GymServiceService.get_by_id(service_id)
    if not service:
        return jsonify(message="Service not found"), 404
    
    # Check if service is available
    if service.status != ServiceStatus.AVAILABLE:
        return jsonify(message="Service is not available"), 400
    
    # Get subscription price based on type
    if subscription_type == SubscriptionType.MONTHLY:
        amount = service.monthly_price
    elif subscription_type == SubscriptionType.QUARTERLY:
        amount = service.quarterly_price
    elif subscription_type == SubscriptionType.ANNUALLY:
        amount = service.annual_price
    else:
        return jsonify(message="Invalid subscription type"), 400
    
    # Process payment
    payment_result, payment_message = WalletService.process_payment(
        user_id, 
        service.provider_id, 
        amount, 
        f"gym_subscription_{service_id}_{user_id}",
        f"Subscription to {service.name} ({subscription_type.value})"
    )
    
    if not payment_result:
        return jsonify(message=payment_message), 400
    
    # Subscribe to gym
    booking_date = datetime.utcnow()
    booking, message = GymServiceService.subscribe_to_gym(user_id, service_id, subscription_type, booking_date, amount, notes)
    if not booking:
        # Refund payment if subscription fails
        WalletService.refund_payment(
            user_id, 
            amount, 
            f"refund_gym_{service_id}_{user_id}",
            f"Refund for failed subscription: {service.name}"
        )
        return jsonify(message=message), 400
    
    return jsonify(message=message, subscription_id=booking.id), 201

@gym_bp.route('/subscriptions/cancel/<int:subscription_id>', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Gym'],
    'summary': 'Cancel subscription',
    'description': 'Cancel a gym service subscription',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'subscription_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Subscription ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Subscription cancelled successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Not authorized'
        },
        '404': {
            'description': 'Subscription not found'
        }
    }
})
def cancel_subscription(subscription_id):
    user_id = get_jwt_identity()
    
    # Cancel subscription
    success, message = GymServiceService.cancel_subscription(user_id, subscription_id)
    if not success:
        if "not authorized" in message.lower():
            return jsonify(message=message), 403
        elif "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    return jsonify(message=message), 200

@gym_bp.route('/subscriptions/active', methods=['GET'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Gym'],
    'summary': 'Get active subscriptions',
    'description': 'Get all active gym subscriptions for current user',
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
            'description': 'List of active subscriptions'
        },
        '403': {
            'description': 'Active user required'
        }
    }
})
def get_active_subscriptions():
    user_id = get_jwt_identity()
    
    subscriptions, message = GymServiceService.get_active_subscriptions(user_id)
    
    # Format subscription data
    result = []
    for sub in subscriptions:
        service = GymServiceService.get_by_id(sub.service_id)
        if service:
            result.append({
                'subscription_id': sub.id,
                'service_id': sub.service_id,
                'service_name': service.name,
                'gym_name': service.gym_name,
                'service_type': service.service_type,
                'subscription_type': sub.subscription_type.value,
                'start_date': sub.subscription_start.isoformat(),
                'end_date': sub.subscription_end.isoformat(),
                'amount_paid': sub.amount
            })
    
    return jsonify(subscriptions=result), 200
