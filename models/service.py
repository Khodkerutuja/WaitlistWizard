from datetime import datetime
from app import db

class ServiceType:
    CAR_POOL = 'CAR_POOL'
    BIKE_POOL = 'BIKE_POOL'
    GYM_FITNESS = 'GYM_FITNESS'
    HOUSEHOLD = 'HOUSEHOLD'
    MECHANICAL = 'MECHANICAL'

class ServiceStatus:
    AVAILABLE = 'AVAILABLE'
    UNAVAILABLE = 'UNAVAILABLE'
    DELETED = 'DELETED'

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=ServiceStatus.AVAILABLE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Common fields for all service types
    location = db.Column(db.String(255), nullable=True)
    availability = db.Column(db.String(255), nullable=True)  # JSON string for complex availability
    
    # Polymorphic relationship
    __mapper_args__ = {
        'polymorphic_on': service_type,
        'polymorphic_identity': 'service'
    }
    
    # Relationships
    provider = db.relationship('User', backref='services')
    bookings = db.relationship('Booking', backref='service', lazy=True)
    feedbacks = db.relationship('Feedback', backref='service', lazy=True)
    
    def __init__(self, name, description, provider_id, service_type, price, location=None, availability=None):
        self.name = name
        self.description = description
        self.provider_id = provider_id
        self.service_type = service_type
        self.price = price
        self.location = location
        self.availability = availability
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'provider_id': self.provider_id,
            'service_type': self.service_type,
            'price': float(self.price),
            'status': self.status,
            'location': self.location,
            'availability': self.availability,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BookingStatus:
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=BookingStatus.PENDING)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bookings')
    
    def __init__(self, user_id, service_id, booking_time, amount):
        self.user_id = user_id
        self.service_id = service_id
        self.booking_time = booking_time
        self.amount = amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'booking_time': self.booking_time.isoformat() if self.booking_time else None,
            'status': self.status,
            'amount': float(self.amount),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
