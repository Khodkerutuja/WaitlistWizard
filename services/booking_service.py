from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from models.booking import Booking
from models.service import Service
from models.user import User
from models.wallet import Wallet
from models.transaction import Transaction
from models.enum_types import BookingStatus, ServiceStatus, UserRole, TransactionType
from app import db

class BookingService:
    @staticmethod
    def get_booking(booking_id):
        """Get booking by ID"""
        return Booking.query.get(booking_id)
    
    @staticmethod
    def get_all_bookings(status=None):
        """Get all bookings with optional status filter"""
        query = Booking.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Booking.created_at.desc()).all()
    
    @staticmethod
    def get_user_bookings(user_id, status=None):
        """Get bookings for a user with optional status filter"""
        query = Booking.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Booking.created_at.desc()).all()
    
    @staticmethod
    def get_provider_bookings(provider_id, status=None):
        """Get bookings for a service provider with optional status filter"""
        query = db.session.query(Booking).join(Service, Booking.service_id == Service.id)
        query = query.filter(Service.provider_id == provider_id)
        if status:
            query = query.filter(Booking.status == status)
        return query.order_by(Booking.created_at.desc()).all()
    
    @staticmethod
    def create_booking(service_id, user_id, quantity=1, notes=None, **kwargs):
        """
        Create a new booking
        
        This handles:
        1. Validating service availability
        2. Calculating the total cost
        3. Creating the booking record (without payment)
        
        Returns the created booking object
        """
        # Get service and check if it's available
        service = Service.query.get(service_id)
        if not service:
            raise ValueError("Service not found")
        
        if service.status != ServiceStatus.AVAILABLE:
            raise ValueError("Service is not available for booking")
        
        # Calculate total amount
        total_amount = service.price * quantity if service.price else 0
        
        # Create booking
        booking = Booking(
            service_id=service_id,
            user_id=user_id,
            amount=total_amount,
            quantity=quantity,
            notes=notes
        )
        
        # Set additional fields from kwargs
        if 'start_time' in kwargs:
            booking.start_time = kwargs['start_time']
        if 'end_time' in kwargs:
            booking.end_time = kwargs['end_time']
        
        # Create the booking (but don't process payment yet)
        db.session.add(booking)
        db.session.commit()
        
        return booking
    
    @staticmethod
    def process_payment(booking_id):
        """
        Process payment for a booking
        
        This handles:
        1. Checking if user has sufficient funds
        2. Processing the payment
        3. Updating booking status to CONFIRMED
        4. Distributing funds (90% to provider, 10% to admin)
        
        Returns a tuple (success, message)
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.status != BookingStatus.PENDING:
            return False, f"Booking is already {booking.status}"
        
        try:
            # Get user and check wallet balance
            user = User.query.get(booking.user_id)
            if not user:
                return False, "User not found"
            
            user_wallet = Wallet.query.filter_by(user_id=user.id).first()
            if not user_wallet:
                return False, "User wallet not found"
            
            if not user_wallet.has_sufficient_funds(booking.amount):
                return False, "Insufficient funds in wallet"
            
            # Get service and provider
            service = Service.query.get(booking.service_id)
            if not service:
                return False, "Service not found"
            
            provider = User.query.get(service.provider_id)
            if not provider:
                return False, "Service provider not found"
            
            provider_wallet = Wallet.query.filter_by(user_id=provider.id).first()
            if not provider_wallet:
                return False, "Provider wallet not found"
            
            # Get admin wallet
            admin = User.query.filter_by(role=UserRole.ADMIN).first()
            if not admin:
                return False, "Admin user not found"
            
            admin_wallet = Wallet.query.filter_by(user_id=admin.id).first()
            if not admin_wallet:
                return False, "Admin wallet not found"
            
            # Calculate commission (10% to admin)
            admin_commission = booking.amount * 0.1
            provider_amount = booking.amount - admin_commission
            
            # Create transaction record for user payment
            user_transaction = Transaction(
                wallet_id=user_wallet.id, 
                amount=booking.amount, 
                transaction_type=TransactionType.PAYMENT,
                description=f"Payment for {service.name}",
                reference_id=str(booking.id)
            )
            db.session.add(user_transaction)
            
            # Create transaction for provider payment
            provider_transaction = Transaction(
                wallet_id=provider_wallet.id,
                amount=provider_amount,
                transaction_type=TransactionType.PAYMENT,
                description=f"Payment received for {service.name}",
                reference_id=str(booking.id)
            )
            db.session.add(provider_transaction)
            
            # Create transaction for admin commission
            admin_transaction = Transaction(
                wallet_id=admin_wallet.id,
                amount=admin_commission,
                transaction_type=TransactionType.COMMISSION,
                description=f"Commission for booking #{booking.id}",
                reference_id=str(booking.id)
            )
            db.session.add(admin_transaction)
            
            # Update wallet balances
            user_wallet.withdraw(booking.amount)
            provider_wallet.deposit(provider_amount)
            admin_wallet.deposit(admin_commission)
            
            # Update booking
            booking.status = BookingStatus.CONFIRMED
            booking.transaction_id = user_transaction.id
            
            db.session.commit()
            return True, "Payment processed successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing payment: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing payment: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def cancel_booking(booking_id):
        """
        Cancel a booking
        
        This handles:
        1. Updating booking status to CANCELLED
        2. Refunding user (if payment was processed)
        
        Returns a tuple (success, message)
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            return False, f"Cannot cancel booking with status {booking.status}"
        
        try:
            # Update booking status
            old_status = booking.status
            booking.status = BookingStatus.CANCELLED
            
            # If payment was processed, issue refund
            if old_status == BookingStatus.CONFIRMED and booking.transaction_id:
                # Get user wallet
                user_wallet = Wallet.query.filter_by(user_id=booking.user_id).first()
                if not user_wallet:
                    return False, "User wallet not found"
                
                # Create refund transaction
                refund_transaction = Transaction(
                    wallet_id=user_wallet.id,
                    amount=booking.amount,
                    transaction_type=TransactionType.REFUND,
                    description=f"Refund for cancelled booking #{booking.id}",
                    reference_id=str(booking.id)
                )
                db.session.add(refund_transaction)
                
                # Update user wallet
                user_wallet.deposit(booking.amount)
                
                # Get service and provider
                service = Service.query.get(booking.service_id)
                provider = User.query.get(service.provider_id)
                provider_wallet = Wallet.query.filter_by(user_id=provider.id).first()
                
                # Get admin wallet
                admin = User.query.filter_by(role=UserRole.ADMIN).first()
                admin_wallet = Wallet.query.filter_by(user_id=admin.id).first()
                
                # Calculate amounts
                admin_commission = booking.amount * 0.1
                provider_amount = booking.amount - admin_commission
                
                # Deduct from provider and admin wallets
                provider_wallet.withdraw(provider_amount)
                admin_wallet.withdraw(admin_commission)
                
                # Create provider and admin transaction records
                provider_refund = Transaction(
                    wallet_id=provider_wallet.id,
                    amount=provider_amount,
                    transaction_type=TransactionType.REFUND,
                    description=f"Deduction for refunded booking #{booking.id}",
                    reference_id=str(booking.id)
                )
                db.session.add(provider_refund)
                
                admin_refund = Transaction(
                    wallet_id=admin_wallet.id,
                    amount=admin_commission,
                    transaction_type=TransactionType.REFUND,
                    description=f"Commission refund for booking #{booking.id}",
                    reference_id=str(booking.id)
                )
                db.session.add(admin_refund)
            
            db.session.commit()
            return True, "Booking cancelled successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error cancelling booking: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error cancelling booking: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def complete_booking(booking_id):
        """Mark a booking as completed"""
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.status != BookingStatus.CONFIRMED:
            return False, f"Cannot complete booking with status {booking.status}"
        
        try:
            booking.status = BookingStatus.COMPLETED
            db.session.commit()
            return True, "Booking marked as completed"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"
    
    @staticmethod
    def reject_booking(booking_id, reason=None):
        """Reject a booking (service provider only)"""
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.status != BookingStatus.PENDING:
            return False, f"Cannot reject booking with status {booking.status}"
        
        try:
            booking.status = BookingStatus.REJECTED
            booking.notes = reason if reason else booking.notes
            db.session.commit()
            return True, "Booking rejected"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"