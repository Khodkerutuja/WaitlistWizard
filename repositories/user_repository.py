from models.user import User, UserRole, UserStatus
from app import db

class UserRepository:
    def create(self, user):
        """
        Create a new user
        
        Args:
            user: User object to create
            
        Returns:
            Created user object
        """
        db.session.add(user)
        db.session.commit()
        return user
    
    def update(self, user):
        """
        Update an existing user
        
        Args:
            user: User object to update
            
        Returns:
            Updated user object
        """
        db.session.commit()
        return user
    
    def delete(self, user):
        """
        Delete a user
        
        Args:
            user: User object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(user)
        db.session.commit()
        return True
    
    def find_by_id(self, user_id):
        """
        Find a user by ID
        
        Args:
            user_id: ID of the user to find
            
        Returns:
            User object if found, None otherwise
        """
        return User.query.get(user_id)
    
    def find_by_email(self, email):
        """
        Find a user by email
        
        Args:
            email: Email of the user to find
            
        Returns:
            User object if found, None otherwise
        """
        return User.query.filter_by(email=email).first()
    
    def find_all(self, role=None, status=None):
        """
        Find all users, optionally filtered by role and/or status
        
        Args:
            role: Filter by role (optional)
            status: Filter by status (optional)
            
        Returns:
            List of user objects
        """
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.all()
    
    def find_service_providers(self, service_type=None, status=None):
        """
        Find all service providers, optionally filtered by service type and/or status
        
        Args:
            service_type: Filter by service type (optional)
            status: Filter by status (optional)
            
        Returns:
            List of service provider user objects
        """
        query = User.query.filter_by(role=UserRole.POWER_USER)
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.all()
    
    def count_all(self):
        """
        Count all users
        
        Returns:
            Number of users
        """
        return User.query.count()
    
    def count_providers(self):
        """
        Count all service providers
        
        Returns:
            Number of service providers
        """
        return User.query.filter_by(role=UserRole.POWER_USER).count()
    
    def count_pending_providers(self):
        """
        Count all pending service providers
        
        Returns:
            Number of pending service providers
        """
        return User.query.filter_by(role=UserRole.POWER_USER, status=UserStatus.PENDING).count()
