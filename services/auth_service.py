from models.user import User, UserRole, UserStatus
from models.wallet import Wallet
from repositories.user_repository import UserRepository
from repositories.wallet_repository import WalletRepository
from werkzeug.security import check_password_hash

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.wallet_repository = WalletRepository()
    
    def register_user(self, email, password, first_name, last_name, phone_number, 
                      address=None, role=UserRole.USER, service_type=None, description=None):
        """
        Register a new user in the system
        
        Args:
            email: User's email address
            password: User's password
            first_name: User's first name
            last_name: User's last name
            phone_number: User's phone number
            address: User's address (optional)
            role: User's role (USER/POWER_USER/ADMIN)
            service_type: Service type (for service providers)
            description: Description of services (for service providers)
            
        Returns:
            Newly created user object
            
        Raises:
            ValueError: If email already exists or other validation fails
        """
        # Check if user exists
        existing_user = self.user_repository.find_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Create user
        user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role
        )
        
        # Set additional fields
        user.address = address
        user.service_type = service_type
        user.description = description
        
        # Save user
        user = self.user_repository.create(user)
        
        # Create wallet for user
        wallet = Wallet(user_id=user.id)
        self.wallet_repository.create(wallet)
        
        return user
    
    def authenticate_user(self, email, password):
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.user_repository.find_by_email(email)
        
        if not user:
            return None
        
        if not user.check_password(password):
            return None
        
        return user
    
    def get_user_by_id(self, user_id):
        """
        Get a user by ID
        
        Args:
            user_id: ID of the user to fetch
            
        Returns:
            User object if found, None otherwise
        """
        return self.user_repository.find_by_id(user_id)
    
    def update_user_profile(self, user_id, first_name=None, last_name=None, 
                           phone_number=None, address=None, description=None):
        """
        Update a user's profile information
        
        Args:
            user_id: ID of the user to update
            first_name: New first name (optional)
            last_name: New last name (optional)
            phone_number: New phone number (optional)
            address: New address (optional)
            description: New description (optional)
            
        Returns:
            Updated user object
            
        Raises:
            ValueError: If user not found
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update fields if provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone_number:
            user.phone_number = phone_number
        if address is not None:  # Allow empty address
            user.address = address
        if description is not None:  # Allow empty description
            user.description = description
        
        # Save updated user
        return self.user_repository.update(user)
    
    def change_password(self, user_id, current_password, new_password):
        """
        Change a user's password
        
        Args:
            user_id: ID of the user
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully, False otherwise
            
        Raises:
            ValueError: If user not found
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Verify current password
        if not user.check_password(current_password):
            return False
        
        # Set new password
        user.set_password(new_password)
        
        # Save updated user
        self.user_repository.update(user)
        return True
