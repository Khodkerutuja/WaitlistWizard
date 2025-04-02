from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from repositories.user_repository import UserRepository
from models import UserRole, UserStatus
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def register_user(username, email, password, role=UserRole.USER):
        """
        Register a new user
        """
        # Check if user already exists
        if UserRepository.get_by_email(email):
            return None, "Email already exists"
        
        if UserRepository.get_by_username(username):
            return None, "Username already exists"
        
        # Set initial status based on role
        status = UserStatus.PENDING if role == UserRole.POWER_USER else UserStatus.ACTIVE
        
        # Create user
        user = UserRepository.create(username, email, password, role, status)
        if not user:
            return None, "Failed to create user"
        
        message = "Registration successful"
        if role == UserRole.POWER_USER:
            message += ". Your account is pending admin approval."
        
        return user, message
    
    @staticmethod
    def login_user(email, password):
        """
        Authenticate and login a user
        """
        user = UserRepository.get_by_email(email)
        if not user or not user.check_password(password):
            return None, "Invalid email or password"
        
        if user.status != UserStatus.ACTIVE:
            return None, "Your account is not active"
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'access_token': access_token
        }, "Login successful"
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change user password
        """
        user = UserRepository.get_by_id(user_id)
        if not user or not user.check_password(current_password):
            return False, "Invalid current password"
        
        # Update password
        user.set_password(new_password)
        updated_user = UserRepository.update(user, {})
        if not updated_user:
            return False, "Failed to update password"
        
        return True, "Password updated successfully"
    
    @staticmethod
    def approve_provider(admin_id, provider_id):
        """
        Approve service provider (admin only)
        """
        # Verify admin
        admin = UserRepository.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return False, "Admin access required"
        
        # Get and verify provider
        provider = UserRepository.get_by_id(provider_id)
        if not provider or provider.role != UserRole.POWER_USER:
            return False, "Invalid provider"
        
        if provider.status != UserStatus.PENDING:
            return False, "Provider is not in pending status"
        
        # Update provider status
        updated_provider = UserRepository.update_status(provider, UserStatus.ACTIVE)
        if not updated_provider:
            return False, "Failed to approve provider"
        
        return True, "Provider approved successfully"
    
    @staticmethod
    def deactivate_provider(admin_id, provider_id):
        """
        Deactivate service provider (admin only)
        """
        # Verify admin
        admin = UserRepository.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return False, "Admin access required"
        
        # Get and verify provider
        provider = UserRepository.get_by_id(provider_id)
        if not provider or provider.role != UserRole.POWER_USER:
            return False, "Invalid provider"
        
        if provider.status != UserStatus.ACTIVE:
            return False, "Provider is not active"
        
        # Update provider status
        updated_provider = UserRepository.update_status(provider, UserStatus.INACTIVE)
        if not updated_provider:
            return False, "Failed to deactivate provider"
        
        return True, "Provider deactivated successfully"
