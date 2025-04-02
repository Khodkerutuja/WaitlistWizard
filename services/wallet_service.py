from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from models.wallet import Wallet, TransactionType
from models.transaction import Transaction
from app import db

class WalletService:
    @staticmethod
    def get_wallet(user_id):
        """Get wallet by user ID"""
        return Wallet.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def get_transactions(wallet_id, limit=5):
        """Get recent transactions for a wallet"""
        return Transaction.query.filter_by(wallet_id=wallet_id).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def add_funds(user_id, amount):
        """
        Add funds to user wallet
        
        Returns a tuple (success, message or wallet)
        """
        if amount <= 0:
            return False, "Amount must be positive"
        
        try:
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not wallet:
                return False, "Wallet not found"
            
            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                description="Funds added to wallet"
            )
            db.session.add(transaction)
            
            # Update wallet balance
            wallet.deposit(amount)
            
            db.session.commit()
            return True, wallet
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding funds: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding funds: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def create_wallet(user_id, initial_balance=0):
        """
        Create a new wallet for a user
        
        Returns a tuple (success, message or wallet)
        """
        try:
            # Check if wallet already exists
            existing_wallet = Wallet.query.filter_by(user_id=user_id).first()
            if existing_wallet:
                return False, "Wallet already exists for this user"
            
            # Create new wallet
            wallet = Wallet(user_id=user_id, initial_balance=initial_balance)
            db.session.add(wallet)
            
            # If initial balance > 0, create transaction record
            if initial_balance > 0:
                transaction = Transaction(
                    wallet_id=wallet.id,
                    amount=initial_balance,
                    transaction_type=TransactionType.DEPOSIT,
                    description="Initial wallet balance"
                )
                db.session.add(transaction)
            
            db.session.commit()
            return True, wallet
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating wallet: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating wallet: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def transfer_funds(from_user_id, to_user_id, amount, description=None):
        """
        Transfer funds between wallets (admin only)
        
        Returns a tuple (success, message)
        """
        if amount <= 0:
            return False, "Amount must be positive"
        
        try:
            # Get source wallet
            from_wallet = Wallet.query.filter_by(user_id=from_user_id).first()
            if not from_wallet:
                return False, "Source wallet not found"
            
            # Get destination wallet
            to_wallet = Wallet.query.filter_by(user_id=to_user_id).first()
            if not to_wallet:
                return False, "Destination wallet not found"
            
            # Check if source wallet has sufficient funds
            if not from_wallet.has_sufficient_funds(amount):
                return False, "Insufficient funds in source wallet"
            
            # Create transaction records
            from_transaction = Transaction(
                wallet_id=from_wallet.id,
                amount=amount,
                transaction_type=TransactionType.WITHDRAWAL,
                description=description or f"Transfer to user {to_user_id}"
            )
            db.session.add(from_transaction)
            
            to_transaction = Transaction(
                wallet_id=to_wallet.id,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                description=description or f"Transfer from user {from_user_id}"
            )
            db.session.add(to_transaction)
            
            # Update wallet balances
            from_wallet.withdraw(amount)
            to_wallet.deposit(amount)
            
            db.session.commit()
            return True, "Funds transferred successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error transferring funds: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error transferring funds: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def adjust_balance(user_id, amount, description=None):
        """
        Adjust wallet balance (admin only)
        
        Amount can be positive or negative
        Returns a tuple (success, message or wallet)
        """
        try:
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not wallet:
                return False, "Wallet not found"
            
            # Create transaction record
            transaction_type = TransactionType.DEPOSIT if amount > 0 else TransactionType.WITHDRAWAL
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=abs(amount),
                transaction_type=transaction_type,
                description=description or "Admin adjustment"
            )
            db.session.add(transaction)
            
            # Update wallet balance
            if amount > 0:
                wallet.deposit(amount)
            else:
                try:
                    wallet.withdraw(abs(amount))
                except ValueError as e:
                    return False, str(e)
            
            db.session.commit()
            return True, wallet
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error adjusting balance: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adjusting balance: {str(e)}")
            return False, f"Error: {str(e)}"