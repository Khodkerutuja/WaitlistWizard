from models.transaction import Transaction
from app import db

class TransactionRepository:
    def create(self, transaction):
        """
        Create a new transaction record
        
        Args:
            transaction: Transaction object to create
            
        Returns:
            Created transaction object
        """
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def find_by_id(self, transaction_id):
        """
        Find a transaction by ID
        
        Args:
            transaction_id: ID of the transaction
            
        Returns:
            Transaction object if found, None otherwise
        """
        return Transaction.query.get(transaction_id)
    
    def find_by_wallet_id(self, wallet_id, limit=None):
        """
        Find transactions for a specific wallet
        
        Args:
            wallet_id: ID of the wallet
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction objects
        """
        query = Transaction.query.filter_by(wallet_id=wallet_id).order_by(Transaction.created_at.desc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def find_by_reference_id(self, reference_id):
        """
        Find transactions by reference ID
        
        Args:
            reference_id: Reference ID to search for
            
        Returns:
            List of transaction objects
        """
        return Transaction.query.filter_by(reference_id=reference_id).all()
    
    def update(self, transaction):
        """
        Update a transaction
        
        Args:
            transaction: Transaction object to update
            
        Returns:
            Updated transaction object
        """
        db.session.commit()
        return transaction
    
    def delete(self, transaction):
        """
        Delete a transaction
        
        Args:
            transaction: Transaction object to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(transaction)
        db.session.commit()
        return True