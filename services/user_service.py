from repositories.user_repository import UserRepository
from models import UserRole, UserStatus
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        """
        return UserRepository.get_by_id(user_id)
    
    @staticmethod
    def get_all_users():
        """
        Get all users
        """
        return UserRepository.get_all()
    
    @staticmethod
    def get_all_providers():
        """
        Get all service providers
        """
        return UserRepository.get_all_providers()
    
    @staticmethod
    def get_pending_providers():
        """
        Get service providers with pending status
        """
        return UserRepository.get_pending_providers()
    
    @staticmethod
    def update_user_profile(user_id, data):
        """
        Update user profile
        """
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Check if email is being updated and is already taken
        if 'email' in data and data['email'] != user.email:
            existing_user = UserRepository.get_by_email(data['email'])
            if existing_user:
                return None, "Email already in use"
        
        # Check if username is being updated and is already taken
        if 'username' in data and data['username'] != user.username:
            existing_user = UserRepository.get_by_username(data['username'])
            if existing_user:
                return None, "Username already in use"
        
        # Update user
        updated_user = UserRepository.update(user, data)
        if not updated_user:
            return None, "Failed to update profile"
        
        return updated_user, "Profile updated successfully"
    
    @staticmethod
    def update_user_role(admin_id, user_id, new_role):
        """
        Update user role (admin only)
        """
        # Verify admin
        admin = UserRepository.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return None, "Admin access required"
        
        # Get and verify user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Cannot change own role
        if admin_id == user_id:
            return None, "Cannot change your own role"
        
        # Update user role
        updated_user = UserRepository.update_role(user, new_role)
        if not updated_user:
            return None, "Failed to update user role"
        
        return updated_user, "User role updated successfully"
    
    @staticmethod
    def update_user_status(admin_id, user_id, new_status):
        """
        Update user status (admin only)
        """
        # Verify admin
        admin = UserRepository.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return None, "Admin access required"
        
        # Get and verify user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Cannot change own status
        if admin_id == user_id:
            return None, "Cannot change your own status"
        
        # Update user status
        updated_user = UserRepository.update_status(user, new_status)
        if not updated_user:
            return None, "Failed to update user status"
        
        return updated_user, "User status updated successfully"
    
    @staticmethod
    def delete_user(admin_id, user_id):
        """
        Delete user (admin only)
        """
        # Verify admin
        admin = UserRepository.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return False, "Admin access required"
        
        # Get and verify user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User not found"
        
        # Cannot delete self
        if admin_id == user_id:
            return False, "Cannot delete your own account"
        
        # Delete user
        success = UserRepository.delete(user)
        if not success:
            return False, "Failed to delete user"
        
        return True, "User deleted successfully"
