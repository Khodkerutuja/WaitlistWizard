from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.service_service import ServiceService
from schemas.service_schema import services_schema, service_schema, service_update_schema
from utils.auth_utils import active_user_required
from models import ServiceCategory
from flasgger import swag_from

services_bp = Blueprint('services', __name__)

@services_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Services'],
    'summary': 'Get all services',
    'description': 'Get all available services',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'category',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by service category'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of services'
        }
    }
})
def get_services():
    category_str = request.args.get('category')
    
    if category_str:
        try:
            category = ServiceCategory(category_str)
            services = ServiceService.get_services_by_category(category)
        except ValueError:
            return jsonify(message="Invalid category"), 400
    else:
        services = ServiceService.get_all_services()
    
    result = services_schema.dump(services)
    return jsonify(services=result), 200

@services_bp.route('/<int:service_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Services'],
    'summary': 'Get service details',
    'description': 'Get service details by ID',
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
            'description': 'Service details'
        },
        '404': {
            'description': 'Service not found'
        }
    }
})
def get_service(service_id):
    service = ServiceService.get_service_by_id(service_id)
    
    if not service:
        return jsonify(message="Service not found"), 404
    
    result = service_schema.dump(service)
    return jsonify(service=result), 200

@services_bp.route('/provider', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Services'],
    'summary': 'Get provider services',
    'description': 'Get services offered by current user (provider)',
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
            'description': 'List of services'
        }
    }
})
def get_provider_services():
    provider_id = get_jwt_identity()
    services = ServiceService.get_services_by_provider(provider_id)
    
    result = services_schema.dump(services)
    return jsonify(services=result), 200

@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Services'],
    'summary': 'Update service',
    'description': 'Update service details (provider only)',
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
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'price': {'type': 'number', 'minimum': 0},
                    'status': {'type': 'string', 'enum': ['available', 'unavailable']}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Service updated successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '403': {
            'description': 'Not authorized'
        },
        '404': {
            'description': 'Service not found'
        }
    }
})
def update_service(service_id):
    provider_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate with schema
    errors = service_update_schema.validate(data)
    if errors:
        return jsonify(errors=errors), 400
    
    # Update service
    updated_service, message = ServiceService.update_service(provider_id, service_id, data)
    if not updated_service:
        if "not authorized" in message.lower():
            return jsonify(message=message), 403
        elif "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    result = service_schema.dump(updated_service)
    return jsonify(message=message, service=result), 200

@services_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Services'],
    'summary': 'Delete service',
    'description': 'Delete a service (provider or admin)',
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
            'description': 'Service deleted successfully'
        },
        '403': {
            'description': 'Not authorized'
        },
        '404': {
            'description': 'Service not found'
        }
    }
})
def delete_service(service_id):
    user_id = get_jwt_identity()
    
    success, message = ServiceService.delete_service(user_id, service_id)
    if not success:
        if "not authorized" in message.lower():
            return jsonify(message=message), 403
        elif "not found" in message.lower():
            return jsonify(message=message), 404
        else:
            return jsonify(message=message), 400
    
    return jsonify(message=message), 200
