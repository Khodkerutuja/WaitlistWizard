from app import db
from models import Service, ServiceCategory, ServiceStatus
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class ServiceRepository:
    @staticmethod
    def get_by_id(service_id):
        try:
            return Service.query.get(service_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching service by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        try:
            return Service.query.filter_by(status=ServiceStatus.AVAILABLE).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all services: {str(e)}")
            return []
    
    @staticmethod
    def get_by_category(category):
        try:
            return Service.query.filter_by(
                category=category,
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching services by category: {str(e)}")
            return []
    
    @staticmethod
    def get_by_provider(provider_id):
        try:
            return Service.query.filter_by(provider_id=provider_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching services by provider: {str(e)}")
            return []
    
    @staticmethod
    def update(service, data):
        try:
            for key, value in data.items():
                setattr(service, key, value)
            
            db.session.commit()
            return service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating service: {str(e)}")
            return None
    
    @staticmethod
    def delete(service):
        try:
            service.status = ServiceStatus.DELETED
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting service: {str(e)}")
            return False
