from repositories.mechanical_repository import MechanicalRepository
from repositories.user_repository import UserRepository
from models import ServiceCategory, ServiceStatus, BookingStatus, UserRole, UserStatus, Booking
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MechanicalServiceService:
    @staticmethod
    def get_by_id(service_id):
        """
        Get mechanical service by ID
        """
        return MechanicalRepository.get_by_id(service_id)
    
    @staticmethod
    def get_all():
        """
        Get all available mechanical services
        """
        return MechanicalRepository.get_all()
    
    @staticmethod
    def get_by_provider(provider_id):
        """
        Get mechanical services by provider
        """
        return MechanicalRepository.get_by_provider(provider_id)
    
    @staticmethod
    def get_by_service_type(service_type):
        """
        Get mechanical services by type (repair, maintenance, etc.)
        """
        return MechanicalRepository.get_by_service_type(service_type)
    
    @staticmethod
    def create_mechanical_service(provider_id, data):
        """
        Create a new mechanical service
        """
        # Verify provider
        provider = UserRepository.get_by_id(provider_id)
        if not provider or provider.role != UserRole.POWER_USER:
            return None, "Invalid service provider"
        
        if provider.status != UserStatus.ACTIVE:
            return None, "Service provider is not active"
        
        # Create service
        service = MechanicalRepository.create(data, provider_id)
        if not service:
            return None, "Failed to create mechanical service"
        
        return service, "Mechanical service created successfully"
    
    @staticmethod
    def update_mechanical_service(provider_id, service_id, data):
        """
        Update mechanical service details
        """
        # Get service
        service = MechanicalRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Verify provider is owner
        if service.provider_id != provider_id:
            return None, "You are not authorized to update this service"
        
        # Update service
        updated_service = MechanicalRepository.update(service, data)
        if not updated_service:
            return None, "Failed to update service"
        
        return updated_service, "Service updated successfully"
    
    @staticmethod
    def book_mechanical_service(user_id, service_id, booking_date, amount, notes=None):
        """
        Book a mechanical service
        """
        # Verify user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Get service
        service = MechanicalRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Check if service is available
        if service.status != ServiceStatus.AVAILABLE:
            return None, "Service is not available"
        
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
            db.session.commit()
            return booking, "Mechanical service booked successfully"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error booking mechanical service: {str(e)}")
            return None, "Failed to book mechanical service"
    
    @staticmethod
    def cancel_booking(user_id, booking_id):
        """
        Cancel a mechanical service booking
        """
        # Get booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        # Verify user is consumer
        if booking.consumer_id != user_id:
            return False, "You are not authorized to cancel this booking"
        
        # Check if booking can be cancelled (not completed or already cancelled)
        if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            return False, "Booking cannot be cancelled"
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        
        try:
            db.session.commit()
            return True, "Booking cancelled successfully"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cancelling booking: {str(e)}")
            return False, "Failed to cancel booking"
    
    @staticmethod
    def update_booking_status(provider_id, booking_id, new_status):
        """
        Update booking status (provider only)
        """
        # Get booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        # Get service
        service = MechanicalRepository.get_by_id(booking.service_id)
        if not service:
            return False, "Service not found"
        
        # Verify provider is owner of service
        if service.provider_id != provider_id:
            return False, "You are not authorized to update this booking"
        
        # Update booking status
        booking.status = new_status
        
        try:
            db.session.commit()
            return True, f"Booking status updated to {new_status.value}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating booking status: {str(e)}")
            return False, "Failed to update booking status"
