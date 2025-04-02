from app import db
from models import GymService, ServiceCategory, ServiceStatus
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class GymRepository:
    @staticmethod
    def get_by_id(service_id):
        try:
            return GymService.query.get(service_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching gym service by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        try:
            return GymService.query.filter_by(
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all gym services: {str(e)}")
            return []
    
    @staticmethod
    def get_by_provider(provider_id):
        try:
            return GymService.query.filter_by(provider_id=provider_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching gym services by provider: {str(e)}")
            return []
    
    @staticmethod
    def get_by_service_type(service_type):
        try:
            return GymService.query.filter_by(
                service_type=service_type,
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching gym services by type: {str(e)}")
            return []
    
    @staticmethod
    def create(data, provider_id):
        try:
            gym_service = GymService(
                name=data['name'],
                description=data['description'],
                category=ServiceCategory.GYM,
                price=data['price'],  # Base price for reference
                provider_id=provider_id,
                status=ServiceStatus.AVAILABLE,
                gym_name=data['gym_name'],
                service_type=data['service_type'],
                trainer_name=data.get('trainer_name', ''),
                monthly_price=data['monthly_price'],
                quarterly_price=data['quarterly_price'],
                annual_price=data['annual_price']
            )
            db.session.add(gym_service)
            db.session.commit()
            return gym_service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating gym service: {str(e)}")
            return None
    
    @staticmethod
    def update(service, data):
        try:
            for key, value in data.items():
                setattr(service, key, value)
            
            db.session.commit()
            return service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating gym service: {str(e)}")
            return None
