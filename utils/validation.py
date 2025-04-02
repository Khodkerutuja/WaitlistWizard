import re
from datetime import datetime

def is_valid_email(email):
    """
    Validate email format
    """
    if not email:
        return False
    
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_password(password):
    """
    Validate password strength
    - At least 6 characters
    """
    if not password or len(password) < 6:
        return False
    
    return True

def is_valid_date_format(date_str, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Validate date format
    """
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

def validate_positive_amount(amount):
    """
    Validate if amount is positive
    """
    try:
        amount_float = float(amount)
        return amount_float > 0
    except (ValueError, TypeError):
        return False
