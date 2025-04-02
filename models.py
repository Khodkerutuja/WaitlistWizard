import enum
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Enums
class UserRole(enum.Enum):
    USER = 'user'           # Service Consumer
    POWER_USER = 'power_user'  # Service Provider
    ADMIN = 'admin'         # Admin

class UserStatus(enum.Enum):
    PENDING = 'pending'
    ACTIVE = 'active'
    INACTIVE = 'inactive'

class ServiceCategory(enum.Enum):
    CAR_POOL = 'car_pool'
    BIKE_POOL = 'bike_pool'
    GYM = 'gym'
    HOUSEHOLD = 'household'
    MECHANICAL = 'mechanical'

class ServiceStatus(enum.Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    DELETED = 'deleted'

class BookingStatus(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class SubscriptionType(enum.Enum):
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    ANNUALLY = 'annually'

class TransactionType(enum.Enum):
    DEPOSIT = 'deposit'
    PAYMENT = 'payment'
    REFUND = 'refund'
    COMMISSION = 'commission'

# Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    status = db.Column(db.Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wallet = db.relationship('Wallet', backref='user', uselist=False, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='consumer', foreign_keys='Booking.consumer_id', lazy='dynamic')
    provided_services = db.relationship('Service', backref='provider', lazy='dynamic')
    feedbacks_given = db.relationship('Feedback', backref='user', foreign_keys='Feedback.user_id', lazy='dynamic')
    feedbacks_received = db.relationship('Feedback', backref='provider', foreign_keys='Feedback.provider_id', lazy='dynamic')
    
    def __init__(self, username, email, password, role=UserRole.USER, status=UserStatus.PENDING):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.status = status
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_provider(self):
        return self.role == UserRole.POWER_USER
    
    def is_consumer(self):
        return self.role == UserRole.USER
    
    def is_active(self):
        return self.status == UserStatus.ACTIVE

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='wallet', lazy='dynamic', cascade='all, delete-orphan')
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        
    def get_last_transactions(self, limit=5):
        return Transaction.query.filter_by(wallet_id=self.id).order_by(Transaction.created_at.desc()).limit(limit).all()

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    description = db.Column(db.String(255))
    reference_id = db.Column(db.String(255))  # For service booking reference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.Enum(ServiceCategory), nullable=False)
    price = db.Column(db.Float, nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(ServiceStatus), default=ServiceStatus.AVAILABLE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Type-specific details (polymorphic)
    type = db.Column(db.String(50))
    
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'service'
    }
    
    # Relationships
    bookings = db.relationship('Booking', backref='service', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='service', lazy='dynamic', cascade='all, delete-orphan')

class CarPoolService(Service):
    __tablename__ = 'car_pool_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    vehicle_type = db.Column(db.String(50), nullable=False)  # car or bike
    vehicle_model = db.Column(db.String(100))
    capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'car_pool'
    }

class GymService(Service):
    __tablename__ = 'gym_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    gym_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)  # fitness, zumba, yoga, etc.
    trainer_name = db.Column(db.String(100))
    monthly_price = db.Column(db.Float, nullable=False)
    quarterly_price = db.Column(db.Float, nullable=False)
    annual_price = db.Column(db.Float, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'gym'
    }

class HouseholdService(Service):
    __tablename__ = 'household_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)  # maid, plumbing, pest control, etc.
    visiting_hours = db.Column(db.String(100))
    
    __mapper_args__ = {
        'polymorphic_identity': 'household'
    }

class MechanicalService(Service):
    __tablename__ = 'mechanical_services'
    
    id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)  # repair, maintenance, etc.
    vehicle_types = db.Column(db.String(255))  # comma-separated types
    
    __mapper_args__ = {
        'polymorphic_identity': 'mechanical'
    }

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    consumer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For gym subscriptions
    subscription_type = db.Column(db.Enum(SubscriptionType), nullable=True)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
