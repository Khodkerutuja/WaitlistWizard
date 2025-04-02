"""
Enumeration types shared across models
Centralizing these here to prevent circular imports
"""

class BookingStatus:
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'
    REJECTED = 'REJECTED'

class TransactionType:
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'
    PAYMENT = 'PAYMENT'
    REFUND = 'REFUND'
    COMMISSION = 'COMMISSION'
    ADMIN_ADJUSTMENT = 'ADMIN_ADJUSTMENT'

class ServiceStatus:
    PENDING = 'PENDING'
    AVAILABLE = 'AVAILABLE'
    UNAVAILABLE = 'UNAVAILABLE'
    DELETED = 'DELETED'

class ServiceType:
    CAR_POOL = 'CAR_POOL'
    BIKE_POOL = 'BIKE_POOL'
    GYM_FITNESS = 'GYM_FITNESS'
    HOUSEHOLD = 'HOUSEHOLD'
    MECHANICAL = 'MECHANICAL'

class UserRole:
    USER = 'USER'
    POWER_USER = 'POWER_USER'
    ADMIN = 'ADMIN'
    
class VehicleType:
    CAR = 'CAR'
    BIKE = 'BIKE'