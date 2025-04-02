from app import db
from models import Feedback, Service
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_
import logging

logger = logging.getLogger(__name__)

class FeedbackRepository:
    @staticmethod
    def get_by_id(feedback_id):
        try:
            return Feedback.query.get(feedback_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching feedback by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_by_service(service_id):
        try:
            return Feedback.query.filter_by(service_id=service_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching feedback by service: {str(e)}")
            return []
    
    @staticmethod
    def get_by_user(user_id):
        try:
            return Feedback.query.filter_by(user_id=user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching feedback by user: {str(e)}")
            return []
    
    @staticmethod
    def get_by_provider(provider_id):
        try:
            return Feedback.query.filter_by(provider_id=provider_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching feedback by provider: {str(e)}")
            return []
    
    @staticmethod
    def create(user_id, service_id, rating, review=None):
        try:
            # Get the service to find the provider
            service = Service.query.get(service_id)
            if not service:
                raise ValueError("Service not found")
            
            feedback = Feedback(
                service_id=service_id,
                user_id=user_id,
                provider_id=service.provider_id,
                rating=rating,
                review=review
            )
            db.session.add(feedback)
            db.session.commit()
            return feedback
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logger.error(f"Error creating feedback: {str(e)}")
            return None
    
    @staticmethod
    def update(feedback, data):
        try:
            for key, value in data.items():
                setattr(feedback, key, value)
            
            db.session.commit()
            return feedback
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating feedback: {str(e)}")
            return None
    
    @staticmethod
    def delete(feedback):
        try:
            db.session.delete(feedback)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting feedback: {str(e)}")
            return False
    
    @staticmethod
    def get_average_rating(service_id):
        try:
            avg_rating = db.session.query(func.avg(Feedback.rating)).filter_by(service_id=service_id).scalar()
            return float(avg_rating) if avg_rating else 0
        except SQLAlchemyError as e:
            logger.error(f"Error getting average rating: {str(e)}")
            return 0
    
    @staticmethod
    def get_average_provider_rating(provider_id):
        try:
            avg_rating = db.session.query(func.avg(Feedback.rating)).filter_by(provider_id=provider_id).scalar()
            return float(avg_rating) if avg_rating else 0
        except SQLAlchemyError as e:
            logger.error(f"Error getting average provider rating: {str(e)}")
            return 0
