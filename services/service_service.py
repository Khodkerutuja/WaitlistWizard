from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from models.service import Service
from models.enum_types import ServiceStatus, ServiceType
from app import db

class ServiceService:
    @staticmethod
    def get_service(service_id):
        """Get service by ID"""
        return Service.query.get(service_id)
    
    @staticmethod
    def get_services(status=None, service_type=None, provider_id=None):
        """Get services with optional filters"""
        query = Service.query
        
        if status:
            query = query.filter_by(status=status)
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        if provider_id:
            query = query.filter_by(provider_id=provider_id)
        
        return query.all()
    
    @staticmethod
    def get_all_services():
        """Get all services (admin)"""
        return Service.query.all()
    
    @staticmethod
    def create_service(data, provider_id):
        """
        Create a new service
        
        Returns a tuple (success, message or service)
        """
        try:
            service = Service()
            service.provider_id = provider_id
            
            # Set service fields
            for key, value in data.items():
                if hasattr(service, key):
                    setattr(service, key, value)
            
            # Default values
            if not service.status:
                service.status = ServiceStatus.PENDING
            
            db.session.add(service)
            db.session.commit()
            return True, service
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating service: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating service: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def update_service(service_id, data, user_id=None, is_admin=False):
        """
        Update a service
        
        If not admin, checks that the provider_id matches the user_id
        Returns a tuple (success, message or service)
        """
        try:
            service = Service.query.get(service_id)
            if not service:
                return False, "Service not found"
            
            # Check if user is authorized to update this service
            if not is_admin and service.provider_id != user_id:
                return False, "Not authorized to update this service"
            
            # Update service fields
            for key, value in data.items():
                if hasattr(service, key):
                    setattr(service, key, value)
            
            db.session.commit()
            return True, service
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating service: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating service: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def delete_service(service_id, user_id=None, is_admin=False):
        """
        Delete a service
        
        If not admin, checks that the provider_id matches the user_id
        Returns a tuple (success, message)
        """
        try:
            service = Service.query.get(service_id)
            if not service:
                return False, "Service not found"
            
            # Check if user is authorized to delete this service
            if not is_admin and service.provider_id != user_id:
                return False, "Not authorized to delete this service"
            
            # For safety, mark as deleted instead of actual deletion
            service.status = ServiceStatus.DELETED
            
            db.session.commit()
            return True, "Service deleted successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting service: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting service: {str(e)}")
            return False, f"Error: {str(e)}"