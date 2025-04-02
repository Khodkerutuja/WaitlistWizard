from repositories.wallet_repository import WalletRepository
from repositories.user_repository import UserRepository
from models import UserRole, TransactionType
import logging

logger = logging.getLogger(__name__)

class WalletService:
    @staticmethod
    def get_wallet(user_id):
        """
        Get wallet for a user
        """
        return WalletRepository.get_by_user_id(user_id)
    
    @staticmethod
    def deposit_funds(user_id, amount):
        """
        Add funds to a user's wallet
        """
        if amount <= 0:
            return None, "Amount must be positive"
        
        wallet = WalletRepository.get_by_user_id(user_id)
        if not wallet:
            return None, "Wallet not found"
        
        transaction = WalletRepository.deposit(
            wallet, 
            amount, 
            description="Wallet deposit"
        )
        
        if not transaction:
            return None, "Failed to deposit funds"
        
        return {
            'wallet_id': wallet.id,
            'balance': wallet.balance,
            'amount_deposited': amount,
            'transaction_id': transaction.id
        }, "Funds deposited successfully"
    
    @staticmethod
    def get_transaction_history(user_id, limit=5):
        """
        Get transaction history for a user
        """
        wallet = WalletRepository.get_by_user_id(user_id)
        if not wallet:
            return [], "Wallet not found"
        
        transactions = WalletRepository.get_transaction_history(wallet.id, limit)
        return transactions, "Transaction history retrieved"
    
    @staticmethod
    def process_payment(consumer_id, provider_id, amount, reference_id, description=None):
        """
        Process payment from consumer to provider with admin commission
        """
        if amount <= 0:
            return None, "Amount must be positive"
        
        # Get wallets
        consumer_wallet = WalletRepository.get_by_user_id(consumer_id)
        provider_wallet = WalletRepository.get_by_user_id(provider_id)
        
        if not consumer_wallet or not provider_wallet:
            return None, "Wallet not found"
        
        # Check if consumer has enough balance
        if consumer_wallet.balance < amount:
            return None, "Insufficient funds"
        
        # Calculate admin commission (10%)
        admin_commission = amount * 0.1
        provider_amount = amount - admin_commission
        
        # Get admin wallet
        admin = UserRepository.get_all()[0]  # Assuming first admin in list
        for user in UserRepository.get_all():
            if user.role == UserRole.ADMIN:
                admin = user
                break
        
        admin_wallet = WalletRepository.get_by_user_id(admin.id)
        if not admin_wallet:
            return None, "Admin wallet not found"
        
        # Withdraw from consumer wallet
        consumer_transaction = WalletRepository.withdraw(
            consumer_wallet,
            amount,
            TransactionType.PAYMENT,
            description=description,
            reference_id=reference_id
        )
        
        if not consumer_transaction:
            return None, "Failed to process payment"
        
        # Credit provider wallet
        provider_transaction = WalletRepository.deposit(
            provider_wallet,
            provider_amount,
            description=f"Payment received: {description}",
            reference_id=reference_id
        )
        
        # Credit admin wallet with commission
        admin_transaction = WalletRepository.deposit(
            admin_wallet,
            admin_commission,
            TransactionType.COMMISSION,
            description=f"Commission from payment: {reference_id}",
            reference_id=reference_id
        )
        
        if not provider_transaction or not admin_transaction:
            # Rollback consumer transaction
            WalletRepository.deposit(
                consumer_wallet,
                amount,
                description=f"Rollback of payment: {reference_id}",
                reference_id=reference_id
            )
            return None, "Failed to complete payment"
        
        return {
            'payment_id': consumer_transaction.id,
            'amount': amount,
            'provider_amount': provider_amount,
            'admin_commission': admin_commission,
            'reference_id': reference_id
        }, "Payment processed successfully"
    
    @staticmethod
    def refund_payment(user_id, amount, reference_id, description=None):
        """
        Refund payment to a user's wallet
        """
        if amount <= 0:
            return None, "Amount must be positive"
        
        wallet = WalletRepository.get_by_user_id(user_id)
        if not wallet:
            return None, "Wallet not found"
        
        transaction = WalletRepository.deposit(
            wallet,
            amount,
            TransactionType.REFUND,
            description=description or "Refund for cancelled service",
            reference_id=reference_id
        )
        
        if not transaction:
            return None, "Failed to process refund"
        
        return {
            'wallet_id': wallet.id,
            'balance': wallet.balance,
            'amount_refunded': amount,
            'transaction_id': transaction.id
        }, "Refund processed successfully"
