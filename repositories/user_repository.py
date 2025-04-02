from app import db
from models import User, UserRole, UserStatus, Wallet
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        try:
            return User.query.get(user_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_by_email(email):
        try:
            return User.query.filter_by(email=email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by email: {str(e)}")
            return None
    
    @staticmethod
    def get_by_username(username):
        try:
            return User.query.filter_by(username=username).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by username: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        try:
            return User.query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all users: {str(e)}")
            return []
    
    @staticmethod
    def get_all_providers():
        try:
            return User.query.filter_by(role=UserRole.POWER_USER).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all providers: {str(e)}")
            return []
    
    @staticmethod
    def get_pending_providers():
        try:
            return User.query.filter_by(
                role=UserRole.POWER_USER, 
                status=UserStatus.PENDING
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching pending providers: {str(e)}")
            return []
    
    @staticmethod
    def create(username, email, password, role=UserRole.USER, status=UserStatus.PENDING):
        try:
            user = User(
                username=username,
                email=email,
                password=password,
                role=role,
                status=status
            )
            db.session.add(user)
            
            # Create wallet for the user
            wallet = Wallet(user=user)
            db.session.add(wallet)
            
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    @staticmethod
    def update(user, data):
        try:
            for key, value in data.items():
                if key == 'password':
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating user: {str(e)}")
            return None
    
    @staticmethod
    def update_status(user, status):
        try:
            user.status = status
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating user status: {str(e)}")
            return None
    
    @staticmethod
    def update_role(user, role):
        try:
            user.role = role
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating user role: {str(e)}")
            return None
    
    @staticmethod
    def delete(user):
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            return False
