from models.booking import Booking
from models.enum_types import BookingStatus
from app import db

class BookingRepository:
    def create(self, booking):
        """
        Create a new booking
        
        Args:
            booking: Booking object to create
            
        Returns:
            Created booking object
        """
        db.session.add(booking)
        db.session.commit()
        return booking
    
    def create_booking(self, user_id, service_id, booking_time, amount, status=BookingStatus.PENDING):
        """
        Create a new booking with parameters
        
        Args:
            user_id: ID of the user making the booking
            service_id: ID of the service being booked
            booking_time: Time of the booking
            amount: Amount paid
            status: Booking status
            
        Returns:
            Created booking object
        """
        booking = Booking(
            user_id=user_id,
            service_id=service_id,
            booking_time=booking_time,
            amount=amount,
            status=status
        )
        
        db.session.add(booking)
        db.session.commit()
        return booking
    
    def update(self, booking):
        """
        Update an existing booking
        
        Args:
            booking: Booking object to update
            
        Returns:
            Updated booking object
        """
        db.session.commit()
        return booking
    
    def delete(self, booking):
        """
        Delete a booking
        
        Args:
            booking: Booking object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(booking)
        db.session.commit()
        return True
    
    def find_by_id(self, booking_id):
        """
        Find a booking by ID
        
        Args:
            booking_id: ID of the booking to find
            
        Returns:
            Booking object if found, None otherwise
        """
        return Booking.query.get(booking_id)
    
    def find_by_user_id(self, user_id, status=None):
        """
        Find bookings for a user
        
        Args:
            user_id: ID of the user
            status: Filter by booking status (optional)
            
        Returns:
            List of booking objects
        """
        query = Booking.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Booking.booking_time.desc()).all()
    
    def find_by_provider_id(self, provider_id, status=None):
        """
        Find bookings for a service provider
        
        Args:
            provider_id: ID of the service provider
            status: Filter by booking status (optional)
            
        Returns:
            List of booking objects
        """
        # Join with Service to find bookings for the provider's services
        query = Booking.query.join(
            Booking.service
        ).filter(
            Booking.service.has(provider_id=provider_id)
        )
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Booking.booking_time.desc()).all()
    
    def find_all(self, status=None):
        """
        Find all bookings, optionally filtered by status
        
        Args:
            status: Filter by booking status (optional)
            
        Returns:
            List of booking objects
        """
        query = Booking.query
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Booking.booking_time.desc()).all()
    
    def find_recent(self, limit=5):
        """
        Find recent bookings
        
        Args:
            limit: Maximum number of bookings to return
            
        Returns:
            List of booking objects
        """
        return Booking.query.order_by(Booking.created_at.desc()).limit(limit).all()
    
    def count_all(self, status=None):
        """
        Count all bookings, optionally filtered by status
        
        Args:
            status: Filter by booking status (optional)
            
        Returns:
            Number of bookings
        """
        query = Booking.query
        
        if status:
            query = query.filter_by(status=status)
        
        return query.count()
