from models.user import UserStatus
from repositories.user_repository import UserRepository
from repositories.service_repository import ServiceRepository
from repositories.booking_repository import BookingRepository
from repositories.transaction_repository import TransactionRepository
from app import db

class AdminService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.service_repository = ServiceRepository()
        self.booking_repository = BookingRepository()
        self.transaction_repository = TransactionRepository()
    
    def get_dashboard_stats(self):
        """
        Get statistics for admin dashboard
        
        Returns:
            Dictionary of statistics
        """
        total_users = self.user_repository.count_all()
        total_providers = self.user_repository.count_providers()
        total_services = self.service_repository.count_all()
        total_bookings = self.booking_repository.count_all()
        total_transactions = self.transaction_repository.count_all()
        
        # Get pending provider approvals
        pending_approvals = self.user_repository.count_pending_providers()
        
        # Get recent bookings
        recent_bookings = self.booking_repository.find_recent(limit=5)
        
        # Get recent transactions
        recent_transactions = self.transaction_repository.find_recent(limit=5)
        
        return {
            'total_users': total_users,
            'total_providers': total_providers,
            'total_services': total_services,
            'total_bookings': total_bookings,
            'total_transactions': total_transactions,
            'pending_approvals': pending_approvals,
            'recent_bookings': [booking.to_dict() for booking in recent_bookings],
            'recent_transactions': [transaction.to_dict() for transaction in recent_transactions]
        }
    
    def get_all_services(self, status=None):
        """
        Get all services, optionally filtered by status
        
        Args:
            status: Filter by service status (optional)
            
        Returns:
            List of service objects
        """
        return self.service_repository.find_all(status=status)
    
    def get_all_bookings(self, status=None):
        """
        Get all bookings, optionally filtered by status
        
        Args:
            status: Filter by booking status (optional)
            
        Returns:
            List of booking objects
        """
        return self.booking_repository.find_all(status=status)
    
    def get_all_transactions(self, transaction_type=None, limit=50):
        """
        Get all transactions, optionally filtered by type and limited
        
        Args:
            transaction_type: Filter by transaction type (optional)
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction objects
        """
        return self.transaction_repository.find_all(transaction_type=transaction_type, limit=limit)
    
    def update_service(self, service_id, data):
        """
        Update a service (Admin access)
        
        Args:
            service_id: ID of the service to update
            data: Dictionary of fields to update
            
        Returns:
            Updated service object
            
        Raises:
            ValueError: If service not found
        """
        # Get service
        service = self.service_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")
        
        # Update fields
        for key, value in data.items():
            if hasattr(service, key):
                setattr(service, key, value)
        
        # Save updated service
        return self.service_repository.update(service)
    
    def delete_service(self, service_id):
        """
        Delete a service (Admin access)
        
        Args:
            service_id: ID of the service to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If service not found
        """
        # Get service
        service = self.service_repository.find_by_id(service_id)
        if not service:
            raise ValueError(f"Service with ID {service_id} not found")
        
        # Delete service
        self.service_repository.delete(service)
        return True
    
    def update_user_status(self, user_id, status):
        """
        Update a user's status (Admin access)
        
        Args:
            user_id: ID of the user to update
            status: New status
            
        Returns:
            Updated user object
            
        Raises:
            ValueError: If user not found or invalid status
        """
        # Validate status
        if status not in [UserStatus.ACTIVE, UserStatus.INACTIVE]:
            raise ValueError(f"Invalid status: {status}")
        
        # Get user
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update status
        user.status = status
        
        # Save updated user
        return self.user_repository.update(user)
