from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User, UserRole

def admin_required():
    """
    A decorator to restrict access to admin users only
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role != UserRole.ADMIN:
                return jsonify(message="Admin access required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def provider_required():
    """
    A decorator to restrict access to service providers only
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role != UserRole.POWER_USER:
                return jsonify(message="Service provider access required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def active_user_required():
    """
    A decorator to restrict access to active users only
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.status != 'active':
                return jsonify(message="Active user status required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
