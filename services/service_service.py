from repositories.service_repository import ServiceRepository
from repositories.user_repository import UserRepository
from models import ServiceStatus, UserRole
import logging

logger = logging.getLogger(__name__)

class ServiceService:
    @staticmethod
    def get_service_by_id(service_id):
        """
        Get service by ID
        """
        return ServiceRepository.get_by_id(service_id)
    
    @staticmethod
    def get_all_services():
        """
        Get all available services
        """
        return ServiceRepository.get_all()
    
    @staticmethod
    def get_services_by_category(category):
        """
        Get services by category
        """
        return ServiceRepository.get_by_category(category)
    
    @staticmethod
    def get_services_by_provider(provider_id):
        """
        Get services offered by a provider
        """
        return ServiceRepository.get_by_provider(provider_id)
    
    @staticmethod
    def update_service(provider_id, service_id, data):
        """
        Update service details (provider only)
        """
        # Get service
        service = ServiceRepository.get_by_id(service_id)
        if not service:
            return None, "Service not found"
        
        # Verify provider is owner of service
        if service.provider_id != provider_id:
            return None, "You are not authorized to update this service"
        
        # Update service
        updated_service = ServiceRepository.update(service, data)
        if not updated_service:
            return None, "Failed to update service"
        
        return updated_service, "Service updated successfully"
    
    @staticmethod
    def delete_service(user_id, service_id):
        """
        Delete service (provider or admin)
        """
        # Get user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User not found"
        
        # Get service
        service = ServiceRepository.get_by_id(service_id)
        if not service:
            return False, "Service not found"
        
        # Verify user is owner or admin
        if service.provider_id != user_id and user.role != UserRole.ADMIN:
            return False, "You are not authorized to delete this service"
        
        # Delete service
        success = ServiceRepository.delete(service)
        if not success:
            return False, "Failed to delete service"
        
        return True, "Service deleted successfully"
