from models.user import User, UserRole, UserStatus
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def get_all_users(self, role=None, status=None):
        """
        Get all users, optionally filtered by role and/or status
        
        Args:
            role: Filter by role (optional)
            status: Filter by status (optional)
            
        Returns:
            List of user objects
        """
        return self.user_repository.find_all(role=role, status=status)
    
    def get_user_by_id(self, user_id):
        """
        Get a user by ID
        
        Args:
            user_id: ID of the user to fetch
            
        Returns:
            User object if found, None otherwise
        """
        return self.user_repository.find_by_id(user_id)
    
    def get_service_providers(self, service_type=None, status=None):
        """
        Get all service providers, optionally filtered by service type and/or status
        
        Args:
            service_type: Filter by service type (optional)
            status: Filter by status (optional)
            
        Returns:
            List of service provider user objects
        """
        # Default status to ACTIVE if not specified
        if status is None:
            status = UserStatus.ACTIVE
            
        return self.user_repository.find_service_providers(
            service_type=service_type, 
            status=status
        )
    
    def approve_service_provider(self, provider_id):
        """
        Approve a service provider
        
        Args:
            provider_id: ID of the service provider to approve
            
        Returns:
            Updated service provider user object
            
        Raises:
            ValueError: If provider not found or not a service provider
        """
        provider = self.user_repository.find_by_id(provider_id)
        
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found")
        
        if provider.role != UserRole.POWER_USER:
            raise ValueError(f"User with ID {provider_id} is not a service provider")
        
        if provider.status != UserStatus.PENDING:
            raise ValueError(f"Provider with ID {provider_id} is not in PENDING status")
        
        # Update provider status to ACTIVE
        provider.status = UserStatus.ACTIVE
        
        # Save updated provider
        return self.user_repository.update(provider)
    
    def deactivate_service_provider(self, provider_id):
        """
        Deactivate a service provider
        
        Args:
            provider_id: ID of the service provider to deactivate
            
        Returns:
            Updated service provider user object
            
        Raises:
            ValueError: If provider not found or not a service provider
        """
        provider = self.user_repository.find_by_id(provider_id)
        
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found")
        
        if provider.role != UserRole.POWER_USER:
            raise ValueError(f"User with ID {provider_id} is not a service provider")
        
        # Update provider status to INACTIVE
        provider.status = UserStatus.INACTIVE
        
        # Save updated provider
        return self.user_repository.update(provider)
