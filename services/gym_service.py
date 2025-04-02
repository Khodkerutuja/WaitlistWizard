from repositories.gym_repository import GymRepository
from repositories.user_repository import UserRepository
from models import ServiceCategory, ServiceStatus, BookingStatus, UserRole, UserStatus, Booking, SubscriptionType
from app import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GymServiceService:
    @staticmethod
    def get_by_id(service_id):
        """
        Get gym service by ID
        """
        return GymRepository.get_by_id(service_id)
    
    @staticmethod
    def get_all():
        """
        Get all available gym services
        """
        return GymRepository.get_all()
    
    @staticmethod
    def get_by_provider(provider_id):
        """
        Get gym services by provider
        """
        return GymRepository.get_by_provider(provider_id)
    
    @staticmethod
    def get_by_service_type(service_type):
        """
        Get gym services by type (fitness, yoga, etc.)
        """
        return GymRepository.get_by_service_type(service_type)
    
    @staticmethod
    def create_gym_service(provider_id, data):
        """
        Create a new gym service
        """
        # Verify provider
        provider = UserRepository.get_by_id(provider_id)
        if not provider or provider.role != UserRole.POWER_USER:
            return None, "Invalid service provider"
        
        if provider.status != UserStatus.ACTIVE:
            return None, "Service provider is not active"
        
        # Create service
        service = GymRepository.create(data, provider_id)
        if not service:
            return None, "Failed to create gym service"
        
        return service, "Gym service created successfully"
    
    @staticmethod
    def update_gym_service(provider_id, service_id, data):
        """
        Update gym service details
        """
        # Get service
        service = GymRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Verify provider is owner
        if service.provider_id != provider_id:
            return None, "You are not authorized to update this service"
        
        # Update service
        updated_service = GymRepository.update(service, data)
        if not updated_service:
            return None, "Failed to update service"
        
        return updated_service, "Service updated successfully"
    
    @staticmethod
    def subscribe_to_gym(user_id, service_id, subscription_type, booking_date, amount, notes=None):
        """
        Subscribe to a gym service
        """
        # Verify user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Get service
        service = GymRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Check if service is available
        if service.status != ServiceStatus.AVAILABLE:
            return None, "Service is not available"
        
        # Check if user already has an active subscription to this service
        existing_subscription = Booking.query.filter_by(
            consumer_id=user_id,
            service_id=service_id,
            status=BookingStatus.CONFIRMED
        ).filter(
            Booking.subscription_end >= datetime.utcnow()
        ).first()
        
        if existing_subscription:
            return None, "You already have an active subscription to this service"
        
        # Calculate subscription end date
        subscription_start = booking_date
        if subscription_type == SubscriptionType.MONTHLY:
            subscription_end = subscription_start + timedelta(days=30)
        elif subscription_type == SubscriptionType.QUARTERLY:
            subscription_end = subscription_start + timedelta(days=90)
        elif subscription_type == SubscriptionType.ANNUALLY:
            subscription_end = subscription_start + timedelta(days=365)
        else:
            return None, "Invalid subscription type"
        
        # Create booking/subscription
        try:
            booking = Booking(
                service_id=service_id,
                consumer_id=user_id,
                booking_date=booking_date,
                status=BookingStatus.CONFIRMED,  # Automatically confirmed for subscriptions
                amount=amount,
                notes=notes,
                subscription_type=subscription_type,
                subscription_start=subscription_start,
                subscription_end=subscription_end
            )
            db.session.add(booking)
            db.session.commit()
            return booking, "Gym subscription successful"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error subscribing to gym: {str(e)}")
            return None, "Failed to subscribe to gym service"
    
    @staticmethod
    def cancel_subscription(user_id, booking_id):
        """
        Cancel a gym subscription
        """
        # Get booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Subscription not found"
        
        # Verify user is consumer
        if booking.consumer_id != user_id:
            return False, "You are not authorized to cancel this subscription"
        
        # Check if subscription can be cancelled
        if booking.status != BookingStatus.CONFIRMED:
            return False, "Subscription cannot be cancelled"
        
        # Update subscription status
        booking.status = BookingStatus.CANCELLED
        booking.subscription_end = datetime.utcnow()  # End subscription immediately
        
        try:
            db.session.commit()
            return True, "Subscription cancelled successfully"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cancelling subscription: {str(e)}")
            return False, "Failed to cancel subscription"
    
    @staticmethod
    def get_active_subscriptions(user_id):
        """
        Get all active gym subscriptions for a user
        """
        try:
            subscriptions = Booking.query.join(
                Booking.service
            ).filter(
                Booking.consumer_id == user_id,
                Booking.status == BookingStatus.CONFIRMED,
                Booking.subscription_end >= datetime.utcnow()
            ).all()
            
            return subscriptions, "Active subscriptions retrieved successfully"
        except Exception as e:
            logger.error(f"Error retrieving active subscriptions: {str(e)}")
            return [], "Failed to retrieve active subscriptions"
