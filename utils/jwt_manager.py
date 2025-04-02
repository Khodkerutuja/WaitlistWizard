from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.user import UserRole, UserStatus

def admin_required(f):
    """
    A decorator to protect endpoints that require admin role
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        # Check if the user is an admin
        if identity['role'] != UserRole.ADMIN:
            return jsonify({"error": "Admin access required"}), 403
        
        # Check if the user is active
        if identity['status'] != UserStatus.ACTIVE:
            return jsonify({"error": "Account is not active"}), 403
            
        return f(*args, **kwargs)
    return decorated

def service_provider_required(f):
    """
    A decorator to protect endpoints that require service provider role
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        # Check if the user is a service provider
        if identity['role'] != UserRole.POWER_USER:
            return jsonify({"error": "Service Provider access required"}), 403
        
        # Check if the user is active
        if identity['status'] != UserStatus.ACTIVE:
            return jsonify({"error": "Account is not active"}), 403
            
        return f(*args, **kwargs)
    return decorated

def active_user_required(f):
    """
    A decorator to ensure the user is active
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        # Check if the user is active
        if identity['status'] != UserStatus.ACTIVE:
            return jsonify({"error": "Account is not active"}), 403
            
        return f(*args, **kwargs)
    return decorated
