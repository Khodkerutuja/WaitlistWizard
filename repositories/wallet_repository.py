from models.wallet import Wallet
from app import db

class WalletRepository:
    def create(self, wallet):
        """
        Create a new wallet
        
        Args:
            wallet: Wallet object to create
            
        Returns:
            Created wallet object
        """
        db.session.add(wallet)
        db.session.commit()
        return wallet
    
    def update(self, wallet):
        """
        Update an existing wallet
        
        Args:
            wallet: Wallet object to update
            
        Returns:
            Updated wallet object
        """
        db.session.commit()
        return wallet
    
    def delete(self, wallet):
        """
        Delete a wallet
        
        Args:
            wallet: Wallet object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(wallet)
        db.session.commit()
        return True
    
    def find_by_id(self, wallet_id):
        """
        Find a wallet by ID
        
        Args:
            wallet_id: ID of the wallet to find
            
        Returns:
            Wallet object if found, None otherwise
        """
        return Wallet.query.get(wallet_id)
    
    def find_by_user_id(self, user_id):
        """
        Find a wallet by user ID
        
        Args:
            user_id: ID of the user
            
        Returns:
            Wallet object if found, None otherwise
        """
        return Wallet.query.filter_by(user_id=user_id).first()
    
    def find_all(self):
        """
        Find all wallets
        
        Returns:
            List of wallet objects
        """
        return Wallet.query.all()
