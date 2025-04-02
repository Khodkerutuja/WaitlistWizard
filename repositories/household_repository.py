from app import db
from models import HouseholdService, ServiceCategory, ServiceStatus
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class HouseholdRepository:
    @staticmethod
    def get_by_id(service_id):
        try:
            return HouseholdService.query.get(service_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching household service by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        try:
            return HouseholdService.query.filter_by(
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all household services: {str(e)}")
            return []
    
    @staticmethod
    def get_by_provider(provider_id):
        try:
            return HouseholdService.query.filter_by(provider_id=provider_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching household services by provider: {str(e)}")
            return []
    
    @staticmethod
    def get_by_service_type(service_type):
        try:
            return HouseholdService.query.filter_by(
                service_type=service_type,
                status=ServiceStatus.AVAILABLE
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching household services by type: {str(e)}")
            return []
    
    @staticmethod
    def create(data, provider_id):
        try:
            household_service = HouseholdService(
                name=data['name'],
                description=data['description'],
                category=ServiceCategory.HOUSEHOLD,
                price=data['price'],
                provider_id=provider_id,
                status=ServiceStatus.AVAILABLE,
                service_type=data['service_type'],
                visiting_hours=data.get('visiting_hours', '')
            )
            db.session.add(household_service)
            db.session.commit()
            return household_service
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating household service: {str(e)}")
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
            logger.error(f"Error updating household service: {str(e)}")
            return None
