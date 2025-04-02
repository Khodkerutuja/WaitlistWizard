from models.feedback import Feedback
from app import db

class FeedbackRepository:
    def create(self, feedback):
        """
        Create a new feedback
        
        Args:
            feedback: Feedback object to create
            
        Returns:
            Created feedback object
        """
        db.session.add(feedback)
        db.session.commit()
        return feedback
    
    def update(self, feedback):
        """
        Update an existing feedback
        
        Args:
            feedback: Feedback object to update
            
        Returns:
            Updated feedback object
        """
        db.session.commit()
        return feedback
    
    def delete(self, feedback):
        """
        Delete a feedback
        
        Args:
            feedback: Feedback object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(feedback)
        db.session.commit()
        return True
    
    def find_by_id(self, feedback_id):
        """
        Find a feedback by ID
        
        Args:
            feedback_id: ID of the feedback to find
            
        Returns:
            Feedback object if found, None otherwise
        """
        return Feedback.query.get(feedback_id)
    
    def find_by_user_id(self, user_id):
        """
        Find feedback given by a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of feedback objects
        """
        return Feedback.query.filter_by(user_id=user_id).all()
    
    def find_by_provider_id(self, provider_id):
        """
        Find feedback for a provider
        
        Args:
            provider_id: ID of the provider
            
        Returns:
            List of feedback objects
        """
        return Feedback.query.filter_by(provider_id=provider_id).all()
    
    def find_by_service_id(self, service_id):
        """
        Find feedback for a service
        
        Args:
            service_id: ID of the service
            
        Returns:
            List of feedback objects
        """
        return Feedback.query.filter_by(service_id=service_id).all()
    
    def find_by_user_service(self, user_id, service_id):
        """
        Find feedback given by a user for a specific service
        
        Args:
            user_id: ID of the user
            service_id: ID of the service
            
        Returns:
            Feedback object if found, None otherwise
        """
        return Feedback.query.filter_by(user_id=user_id, service_id=service_id).first()
