from models.wallet import Wallet, TransactionType
from models.transaction import Transaction
from repositories.wallet_repository import WalletRepository
from repositories.user_repository import UserRepository
from repositories.transaction_repository import TransactionRepository
from app import db

class WalletService:
    def __init__(self):
        self.wallet_repository = WalletRepository()
        self.user_repository = UserRepository()
        self.transaction_repository = TransactionRepository()
    
    def get_wallet_by_user_id(self, user_id):
        """
        Get a wallet by user ID
        
        Args:
            user_id: ID of the user
            
        Returns:
            Wallet object if found, None otherwise
        """
        return self.wallet_repository.find_by_user_id(user_id)
    
    def deposit_to_wallet(self, user_id, amount, description="Wallet deposit"):
        """
        Add money to a user's wallet
        
        Args:
            user_id: ID of the user
            amount: Amount to deposit
            description: Transaction description
            
        Returns:
            Tuple of (wallet, transaction) after deposit
            
        Raises:
            ValueError: If user not found or amount is invalid
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # Get wallet
        wallet = self.wallet_repository.find_by_user_id(user_id)
        if not wallet:
            raise ValueError(f"Wallet not found for user {user_id}")
        
        # Start transaction
        try:
            # Add money to wallet
            wallet.deposit(amount)
            
            # Save wallet
            self.wallet_repository.update(wallet)
            
            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                description=description
            )
            
            # Save transaction
            transaction = self.transaction_repository.create(transaction)
            
            return wallet, transaction
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_transaction_history(self, user_id, limit=5):
        """
        Get transaction history for a user's wallet
        
        Args:
            user_id: ID of the user
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction objects
            
        Raises:
            ValueError: If wallet not found
        """
        # Get wallet
        wallet = self.wallet_repository.find_by_user_id(user_id)
        if not wallet:
            raise ValueError(f"Wallet not found for user {user_id}")
        
        # Get transactions
        return self.transaction_repository.find_by_wallet_id(wallet.id, limit)
    
    def admin_adjust_wallet(self, user_id, amount, description):
        """
        Admin adjustment to a user's wallet
        
        Args:
            user_id: ID of the user
            amount: Amount to adjust (positive or negative)
            description: Description of the adjustment
            
        Returns:
            Tuple of (wallet, transaction) after adjustment
            
        Raises:
            ValueError: If user not found or other validation fails
        """
        # Get wallet
        wallet = self.wallet_repository.find_by_user_id(user_id)
        if not wallet:
            raise ValueError(f"Wallet not found for user {user_id}")
        
        # Start transaction
        try:
            if amount > 0:
                # Add money to wallet
                wallet.deposit(amount)
            else:
                # Remove money from wallet (amount is negative)
                try:
                    wallet.withdraw(abs(amount))
                except ValueError as e:
                    raise ValueError(f"Cannot withdraw {abs(amount)}: {str(e)}")
            
            # Save wallet
            self.wallet_repository.update(wallet)
            
            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.ADMIN_ADJUSTMENT,
                description=description
            )
            
            # Save transaction
            transaction = self.transaction_repository.create(transaction)
            
            return wallet, transaction
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def transfer_payment(self, from_user_id, to_user_id, amount, reference_id, admin_commission_percent=10):
        """
        Transfer payment from one user to another with admin commission
        
        Args:
            from_user_id: ID of the user making the payment
            to_user_id: ID of the user receiving the payment
            amount: Amount to transfer
            reference_id: Reference ID (e.g. booking ID)
            admin_commission_percent: Admin commission percentage
            
        Returns:
            True if transfer successful, False otherwise
            
        Raises:
            ValueError: If user not found, insufficient funds, or other validation fails
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        # Get user wallets
        from_wallet = self.wallet_repository.find_by_user_id(from_user_id)
        to_wallet = self.wallet_repository.find_by_user_id(to_user_id)
        
        # Get admin wallet (assuming admin has user_id=1)
        admin_wallet = self.wallet_repository.find_by_user_id(1)
        
        if not from_wallet:
            raise ValueError(f"Wallet not found for user {from_user_id}")
        
        if not to_wallet:
            raise ValueError(f"Wallet not found for user {to_user_id}")
        
        if not admin_wallet:
            raise ValueError("Admin wallet not found")
        
        # Check if user has sufficient funds
        if not from_wallet.has_sufficient_funds(amount):
            raise ValueError("Insufficient funds in wallet")
        
        # Calculate admin commission
        admin_amount = (amount * admin_commission_percent) / 100
        provider_amount = amount - admin_amount
        
        # Start transaction
        try:
            # Remove money from user wallet
            from_wallet.withdraw(amount)
            self.wallet_repository.update(from_wallet)
            
            # Create transaction record for user payment
            user_transaction = Transaction(
                wallet_id=from_wallet.id,
                amount=-amount,
                transaction_type=TransactionType.PAYMENT,
                description=f"Payment for service",
                reference_id=reference_id
            )
            self.transaction_repository.create(user_transaction)
            
            # Add provider's share to provider wallet
            to_wallet.deposit(provider_amount)
            self.wallet_repository.update(to_wallet)
            
            # Create transaction record for provider
            provider_transaction = Transaction(
                wallet_id=to_wallet.id,
                amount=provider_amount,
                transaction_type=TransactionType.PAYMENT,
                description=f"Payment received for service",
                reference_id=reference_id
            )
            self.transaction_repository.create(provider_transaction)
            
            # Add admin commission to admin wallet
            admin_wallet.deposit(admin_amount)
            self.wallet_repository.update(admin_wallet)
            
            # Create transaction record for admin commission
            admin_transaction = Transaction(
                wallet_id=admin_wallet.id,
                amount=admin_amount,
                transaction_type=TransactionType.COMMISSION,
                description=f"Commission from service payment",
                reference_id=reference_id
            )
            self.transaction_repository.create(admin_transaction)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def refund_payment(self, user_id, amount, reference_id, description="Refund for cancelled service"):
        """
        Refund a payment to a user's wallet
        
        Args:
            user_id: ID of the user to refund
            amount: Amount to refund
            reference_id: Reference ID (e.g. booking ID)
            description: Transaction description
            
        Returns:
            Tuple of (wallet, transaction) after refund
            
        Raises:
            ValueError: If user not found or amount is invalid
        """
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        # Get wallet
        wallet = self.wallet_repository.find_by_user_id(user_id)
        if not wallet:
            raise ValueError(f"Wallet not found for user {user_id}")
        
        # Start transaction
        try:
            # Add money to wallet
            wallet.deposit(amount)
            
            # Save wallet
            self.wallet_repository.update(wallet)
            
            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.REFUND,
                description=description,
                reference_id=reference_id
            )
            
            # Save transaction
            transaction = self.transaction_repository.create(transaction)
            
            return wallet, transaction
            
        except Exception as e:
            db.session.rollback()
            raise e
