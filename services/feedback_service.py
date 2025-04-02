from repositories.feedback_repository import FeedbackRepository
from repositories.user_repository import UserRepository
from repositories.service_repository import ServiceRepository
from models import Booking, BookingStatus
import logging

logger = logging.getLogger(__name__)

class FeedbackService:
    @staticmethod
    def get_feedback_by_id(feedback_id):
        """
        Get feedback by ID
        """
        return FeedbackRepository.get_by_id(feedback_id)
    
    @staticmethod
    def get_feedback_by_service(service_id):
        """
        Get all feedback for a service
        """
        return FeedbackRepository.get_by_service(service_id)
    
    @staticmethod
    def get_feedback_by_user(user_id):
        """
        Get all feedback provided by a user
        """
        return FeedbackRepository.get_by_user(user_id)
    
    @staticmethod
    def get_feedback_by_provider(provider_id):
        """
        Get all feedback for a service provider
        """
        return FeedbackRepository.get_by_provider(provider_id)
    
    @staticmethod
    def create_feedback(user_id, service_id, rating, review=None):
        """
        Create feedback for a service
        """
        # Verify user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Get service
        service = ServiceRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Check if user has used this service (completed booking)
        booking = Booking.query.filter_by(
            consumer_id=user_id,
            service_id=service_id,
            status=BookingStatus.COMPLETED
        ).first()
        
        if not booking:
            return None, "You can only review services you have used"
        
        # Check if user has already provided feedback for this service
        existing_feedback = FeedbackRepository.get_by_service(service_id)
        for feedback in existing_feedback:
            if feedback.user_id == user_id:
                return None, "You have already provided feedback for this service"
        
        # Create feedback
        feedback = FeedbackRepository.create(user_id, service_id, rating, review)
        if not feedback:
            return None, "Failed to create feedback"
        
        return feedback, "Feedback submitted successfully"
    
    @staticmethod
    def update_feedback(user_id, feedback_id, data):
        """
        Update feedback
        """
        # Get feedback
        feedback = FeedbackRepository.get_by_id(feedback_id)
        if not feedback:
            return None, "Feedback not found"
        
        # Verify user is owner of feedback
        if feedback.user_id != user_id:
            return None, "You are not authorized to update this feedback"
        
        # Update feedback
        updated_feedback = FeedbackRepository.update(feedback, data)
        if not updated_feedback:
            return None, "Failed to update feedback"
        
        return updated_feedback, "Feedback updated successfully"
    
    @staticmethod
    def delete_feedback(user_id, feedback_id):
        """
        Delete feedback
        """
        # Get feedback
        feedback = FeedbackRepository.get_by_id(feedback_id)
        if not feedback:
            return False, "Feedback not found"
        
        # Verify user is owner of feedback
        if feedback.user_id != user_id:
            return False, "You are not authorized to delete this feedback"
        
        # Delete feedback
        success = FeedbackRepository.delete(feedback)
        if not success:
            return False, "Failed to delete feedback"
        
        return True, "Feedback deleted successfully"
    
    @staticmethod
    def get_service_average_rating(service_id):
        """
        Get average rating for a service
        """
        return FeedbackRepository.get_average_rating(service_id)
    
    @staticmethod
    def get_provider_average_rating(provider_id):
        """
        Get average rating for a service provider
        """
        return FeedbackRepository.get_average_provider_rating(provider_id)
