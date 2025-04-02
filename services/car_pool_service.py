from repositories.car_pool_repository import CarPoolRepository
from repositories.user_repository import UserRepository
from repositories.service_repository import ServiceRepository
from models import ServiceCategory, ServiceStatus, BookingStatus, UserRole, UserStatus, Booking
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CarPoolServiceService:
    @staticmethod
    def get_by_id(service_id):
        """
        Get car pool service by ID
        """
        return CarPoolRepository.get_by_id(service_id)
    
    @staticmethod
    def get_all():
        """
        Get all available car pool services
        """
        return CarPoolRepository.get_all()
    
    @staticmethod
    def get_by_provider(provider_id):
        """
        Get car pool services by provider
        """
        return CarPoolRepository.get_by_provider(provider_id)
    
    @staticmethod
    def search_rides(source, destination, departure_date):
        """
        Search for available rides
        """
        return CarPoolRepository.get_available_rides(source, destination, departure_date)
    
    @staticmethod
    def create_car_pool_service(provider_id, data):
        """
        Create a new car pool service
        """
        # Verify provider
        provider = UserRepository.get_by_id(provider_id)
        if not provider or provider.role != UserRole.POWER_USER:
            return None, "Invalid service provider"
        
        if provider.status != UserStatus.ACTIVE:
            return None, "Service provider is not active"
        
        # Validate capacity and available seats
        if data.get('available_seats', 0) > data.get('capacity', 0):
            return None, "Available seats cannot exceed capacity"
        
        # Create service
        service = CarPoolRepository.create(data, provider_id)
        if not service:
            return None, "Failed to create car pool service"
        
        return service, "Car pool service created successfully"
    
    @staticmethod
    def update_car_pool_service(provider_id, service_id, data):
        """
        Update car pool service details
        """
        # Get service
        service = CarPoolRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Verify provider is owner
        if service.provider_id != provider_id:
            return None, "You are not authorized to update this service"
        
        # Update service
        updated_service = CarPoolRepository.update(service, data)
        if not updated_service:
            return None, "Failed to update service"
        
        return updated_service, "Service updated successfully"
    
    @staticmethod
    def book_ride(user_id, service_id, booking_date, amount, notes=None):
        """
        Book a car/bike ride
        """
        # Verify user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Get service
        service = CarPoolRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Check if service is available
        if service.status != ServiceStatus.AVAILABLE:
            return None, "Service is not available"
        
        # Check if there are available seats
        if service.available_seats <= 0:
            return None, "No available seats"
        
        # Create booking
        try:
            booking = Booking(
                service_id=service_id,
                consumer_id=user_id,
                booking_date=booking_date,
                status=BookingStatus.PENDING,
                amount=amount,
                notes=notes
            )
            db.session.add(booking)
            
            # Update available seats
            service = CarPoolRepository.update_available_seats(service)
            if not service:
                db.session.rollback()
                return None, "Failed to update available seats"
            
            db.session.commit()
            return booking, "Ride booked successfully"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error booking ride: {str(e)}")
            return None, "Failed to book ride"
    
    @staticmethod
    def cancel_booking(user_id, booking_id):
        """
        Cancel a ride booking
        """
        # Get booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        # Verify user is consumer
        if booking.consumer_id != user_id:
            return False, "You are not authorized to cancel this booking"
        
        # Check if booking can be cancelled (not completed)
        if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            return False, "Booking cannot be cancelled"
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        
        # Get service and update available seats
        service = CarPoolRepository.get_by_id(booking.service_id)
        if not service:
            db.session.rollback()
            return False, "Service not found"
        
        service = CarPoolRepository.cancel_booking(service)
        if not service:
            db.session.rollback()
            return False, "Failed to update available seats"
        
        try:
            db.session.commit()
            return True, "Booking cancelled successfully"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cancelling booking: {str(e)}")
            return False, "Failed to cancel booking"
