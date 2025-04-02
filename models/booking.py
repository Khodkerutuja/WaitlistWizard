from datetime import datetime
from app import db
from models.enum_types import BookingStatus

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default=BookingStatus.PENDING)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1)  # For number of seats, hours, etc.
    start_time = db.Column(db.DateTime, nullable=True)  # For scheduled services
    end_time = db.Column(db.DateTime, nullable=True)  # For services with duration
    notes = db.Column(db.Text, nullable=True)  # Additional booking notes
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    # Remove the backref to avoid circular definition with Service model
    service = db.relationship('Service', foreign_keys="Booking.service_id", lazy=True)
    transaction = db.relationship('Transaction', backref=db.backref('booking', uselist=False), lazy=True)
    
    def __init__(self, service_id, user_id, amount, quantity=1, notes=None, status=BookingStatus.PENDING, booking_time=None, start_time=None, end_time=None):
        self.service_id = service_id
        self.user_id = user_id
        self.amount = amount
        self.quantity = quantity
        self.notes = notes
        self.status = status
        self.booking_time = booking_time
        self.start_time = start_time
        self.end_time = end_time
    
    def cancel(self):
        """Cancel a booking"""
        if self.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise ValueError(f"Cannot cancel booking with status {self.status}")
        self.status = BookingStatus.CANCELLED
    
    def confirm(self):
        """Confirm a booking"""
        if self.status != BookingStatus.PENDING:
            raise ValueError(f"Cannot confirm booking with status {self.status}")
        self.status = BookingStatus.CONFIRMED
    
    def complete(self):
        """Mark a booking as completed"""
        if self.status != BookingStatus.CONFIRMED:
            raise ValueError(f"Cannot complete booking with status {self.status}")
        self.status = BookingStatus.COMPLETED
    
    def reject(self):
        """Reject a booking"""
        if self.status != BookingStatus.PENDING:
            raise ValueError(f"Cannot reject booking with status {self.status}")
        self.status = BookingStatus.REJECTED
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'user_id': self.user_id,
            'booking_time': self.booking_time.isoformat() if self.booking_time else None,
            'status': self.status,
            'amount': float(self.amount),
            'quantity': self.quantity,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'notes': self.notes,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }