from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserRole:
    USER = 'USER'        # Service Consumer
    POWER_USER = 'POWER_USER'  # Service Provider
    ADMIN = 'ADMIN'      # Admin

class UserStatus:
    PENDING = 'PENDING'
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(10), nullable=False, default=UserRole.USER)
    status = db.Column(db.String(10), nullable=False, default=UserStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Service Provider specific fields
    service_type = db.Column(db.String(50), nullable=True)  # For service providers
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    wallet = db.relationship('Wallet', backref='user', uselist=False, lazy=True)
    feedbacks_given = db.relationship('Feedback', foreign_keys='Feedback.user_id', backref='user', lazy=True)
    feedbacks_received = db.relationship('Feedback', foreign_keys='Feedback.provider_id', backref='provider', lazy=True)
    
    def __init__(self, email, password, first_name, last_name, phone_number, role=UserRole.USER):
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.role = role
        
        # If it's a service provider, set status to pending
        if role == UserRole.POWER_USER:
            self.status = UserStatus.PENDING
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_service_provider(self):
        return self.role == UserRole.POWER_USER
    
    def is_active(self):
        return self.status == UserStatus.ACTIVE
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'address': self.address,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'service_type': self.service_type,
            'description': self.description
        }
