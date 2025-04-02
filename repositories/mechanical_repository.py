from app import db
from models import MechanicalService, ServiceCategory, ServiceStatus
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class MechanicalRepository:
    @staticmethod
    def get_by_id(service_id):
        try:
            return MechanicalService.query.get(service_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching mechanical service by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        try:
            return MechanicalService.query.filter_by(
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all mechanical services: {str(e)}")
            return []
    
    @staticmethod
    def get_by_provider(provider_id):
        try:
            return MechanicalService.query.filter_by(provider_id=provider_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching mechanical services by provider: {str(e)}")
            return []
    
    @staticmethod
    def get_by_service_type(service_type):
        try:
            return MechanicalService.query.filter_by(
                service_type=service_type,
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching mechanical services by type: {str(e)}")
            return []
    
    @staticmethod
    def create(data, provider_id):
        try:
            mechanical_service = MechanicalService(
                name=data['name'],
                description=data['description'],
                category=ServiceCategory.MECHANICAL,
                price=data['price'],
                provider_id=provider_id,
                status=ServiceStatus.AVAILABLE,
                service_type=data['service_type'],
                vehicle_types=data.get('vehicle_types', '')
            )
            db.session.add(mechanical_service)
            db.session.commit()
            return mechanical_service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating mechanical service: {str(e)}")
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
            logger.error(f"Error updating mechanical service: {str(e)}")
            return None
