from app import db
from models import Wallet, Transaction, TransactionType
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class WalletRepository:
    @staticmethod
    def get_by_id(wallet_id):
        try:
            return Wallet.query.get(wallet_id)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching wallet by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_by_user_id(user_id):
        try:
            return Wallet.query.filter_by(user_id=user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching wallet by user ID: {str(e)}")
            return None
    
    @staticmethod
    def create(user_id, initial_balance=0.0):
        try:
            wallet = Wallet(user_id=user_id, balance=initial_balance)
            db.session.add(wallet)
            db.session.commit()
            return wallet
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating wallet: {str(e)}")
            return None
    
    @staticmethod
    def update_balance(wallet, new_balance):
        try:
            wallet.balance = new_balance
            db.session.commit()
            return wallet
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating wallet balance: {str(e)}")
            return None
    
    @staticmethod
    def deposit(wallet, amount, description=None, reference_id=None):
        try:
            # Ensure amount is positive
            if amount <= 0:
                raise ValueError("Deposit amount must be positive")
            
            # Update wallet balance
            wallet.balance += amount
            
            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                description=description,
                reference_id=reference_id
            )
            db.session.add(transaction)
            
            db.session.commit()
            return transaction
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logger.error(f"Error depositing to wallet: {str(e)}")
            return None
    
    @staticmethod
    def withdraw(wallet, amount, transaction_type=TransactionType.PAYMENT, description=None, reference_id=None):
        try:
            # Ensure amount is positive and sufficient balance exists
            if amount <= 0:
                raise ValueError("Withdrawal amount must be positive")
            
            if amount > wallet.balance:
                raise ValueError("Insufficient funds")
            
            # Update wallet balance
            wallet.balance -= amount
            
            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                reference_id=reference_id
            )
            db.session.add(transaction)
            
            db.session.commit()
            return transaction
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logger.error(f"Error withdrawing from wallet: {str(e)}")
            return None
    
    @staticmethod
    def transfer(from_wallet, to_wallet, amount, description=None, reference_id=None):
        try:
            # Ensure amount is positive and sufficient balance exists
            if amount <= 0:
                raise ValueError("Transfer amount must be positive")
            
            if amount > from_wallet.balance:
                raise ValueError("Insufficient funds")
            
            # Update wallet balances
            from_wallet.balance -= amount
            to_wallet.balance += amount
            
            # Create transaction records
            from_transaction = Transaction(
                wallet_id=from_wallet.id,
                amount=amount,
                transaction_type=TransactionType.PAYMENT,
                description=description,
                reference_id=reference_id
            )
            db.session.add(from_transaction)
            
            to_transaction = Transaction(
                wallet_id=to_wallet.id,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                description=description,
                reference_id=reference_id
            )
            db.session.add(to_transaction)
            
            db.session.commit()
            return (from_transaction, to_transaction)
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logger.error(f"Error transferring between wallets: {str(e)}")
            return None
    
    @staticmethod
    def get_transaction_history(wallet_id, limit=5):
        try:
            return Transaction.query.filter_by(wallet_id=wallet_id).order_by(Transaction.created_at.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching transaction history: {str(e)}")
            return []
