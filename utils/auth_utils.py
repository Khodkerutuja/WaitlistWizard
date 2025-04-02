from functools import wraps
from flask import jsonify
from flask_login import current_user
from models.user import UserRole

def admin_required(f):
    """
    Decorator for routes that require admin access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def service_provider_required(f):
    """
    Decorator for routes that require service provider access (POWER_USER or ADMIN)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if current_user.role not in [UserRole.POWER_USER, UserRole.ADMIN]:
            return jsonify({'error': 'Service provider access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function