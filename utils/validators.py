import re
from flask import request, jsonify
from functools import wraps

def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic email validation regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Password should be at least 8 characters
    if len(password) < 8:
        return False
    
    # Check for at least one letter
    if not re.search(r'[a-zA-Z]', password):
        return False
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_phone_number(phone_number):
    """
    Validate phone number format
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic phone number validation - allows various formats
    pattern = r'^[+]?[\d\s()-]{6,15}$'
    return re.match(pattern, phone_number) is not None

def required_params(*params):
    """
    Decorator to validate required request parameters
    
    Args:
        *params: Required parameter names
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                missing = [param for param in params if param not in data or data[param] == '']
                if missing:
                    return jsonify({
                        'error': 'Missing required parameters',
                        'missing': missing
                    }), 400
            else:
                # Check for form data or query parameters
                data = request.form if request.method in ['POST', 'PUT'] else request.args
                missing = [param for param in params if param not in data or data[param] == '']
                if missing:
                    return jsonify({
                        'error': 'Missing required parameters',
                        'missing': missing
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json():
    """
    Decorator to validate that request contains JSON data
    
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Missing JSON in request'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator
