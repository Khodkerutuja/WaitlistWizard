from models.feedback import Feedback
from models.service import Service
from repositories.feedback_repository import FeedbackRepository
from repositories.service_repository import ServiceRepository
from repositories.user_repository import UserRepository
from app import db

class FeedbackService:
    def __init__(self):
        self.feedback_repository = FeedbackRepository()
        self.service_repository = ServiceRepository()
        self.user_repository = UserRepository()
    
    def add_feedback(self, user_id, service_id, rating, review=None):
        """
        Add feedback for a service
        
        Args:
            user_id: ID of the user giving feedback
            service_id: ID of the service being reviewed
            rating: Rating (1-5)
            review: Text review (optional)
            
        Returns:
            Newly created feedback object
            
        Raises:
            ValueError: If service not found, invalid rating, or other validation fails
        """
        # Validate rating
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Get service
        service = self.service_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")
        
        # Get provider ID from service
        provider_id = service.provider_id
        
        # Check if user has already given feedback for this service
        existing_feedback = self.feedback_repository.find_by_user_service(user_id, service_id)
        if existing_feedback:
            raise ValueError("You have already provided feedback for this service")
        
        try:
            # Create feedback
            feedback = Feedback(
                user_id=user_id,
                provider_id=provider_id,
                service_id=service_id,
                rating=rating,
                review=review
            )
            
            # Save feedback
            return self.feedback_repository.create(feedback)
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_service_feedback(self, service_id):
        """
        Get feedback for a specific service
        
        Args:
            service_id: ID of the service
            
        Returns:
            List of feedback objects
            
        Raises:
            ValueError: If service not found
        """
        # Check if service exists
        service = self.service_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")
        
        return self.feedback_repository.find_by_service_id(service_id)
    
    def get_provider_feedback(self, provider_id):
        """
        Get feedback for a specific service provider
        
        Args:
            provider_id: ID of the service provider
            
        Returns:
            List of feedback objects
            
        Raises:
            ValueError: If provider not found
        """
        # Check if provider exists
        provider = self.user_repository.find_by_id(provider_id)
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found")
        
        return self.feedback_repository.find_by_provider_id(provider_id)
    
    def get_user_feedback(self, user_id):
        """
        Get feedback given by a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of feedback objects
        """
        return self.feedback_repository.find_by_user_id(user_id)
    
    def update_feedback(self, feedback_id, user_id, rating=None, review=None):
        """
        Update a feedback
        
        Args:
            feedback_id: ID of the feedback to update
            user_id: ID of the user updating the feedback (for authorization)
            rating: New rating (optional)
            review: New review (optional)
            
        Returns:
            Updated feedback object
            
        Raises:
            ValueError: If feedback not found, user not authorized, or invalid rating
        """
        # Get feedback
        feedback = self.feedback_repository.find_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback with ID {feedback_id} not found")
        
        # Check if user is authorized
        if feedback.user_id != user_id:
            raise ValueError("Not authorized to update this feedback")
        
        # Update fields
        if rating is not None:
            # Validate rating
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            feedback.rating = rating
        
        if review is not None:
            feedback.review = review
        
        # Save updated feedback
        return self.feedback_repository.update(feedback)
    
    def delete_feedback(self, feedback_id, user_id, role):
        """
        Delete a feedback
        
        Args:
            feedback_id: ID of the feedback to delete
            user_id: ID of the user deleting the feedback (for authorization)
            role: Role of the user
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If feedback not found or user not authorized
        """
        # Get feedback
        feedback = self.feedback_repository.find_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback with ID {feedback_id} not found")
        
        # Check if user is authorized (user who gave the feedback or admin)
        if feedback.user_id != user_id and role != 'ADMIN':
            raise ValueError("Not authorized to delete this feedback")
        
        # Delete feedback
        self.feedback_repository.delete(feedback)
        return True
