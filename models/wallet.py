from datetime import datetime
from app import db
from models.enum_types import TransactionType

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='wallet', lazy=True)
    
    def __init__(self, user_id, initial_balance=0):
        self.user_id = user_id
        self.balance = initial_balance
    
    def deposit(self, amount):
        """Add money to wallet"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
    
    def withdraw(self, amount):
        """Remove money from wallet"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
    
    def has_sufficient_funds(self, amount):
        """Check if wallet has sufficient funds"""
        return self.balance >= amount
    
    def get_recent_transactions(self, limit=5):
        """Get recent transactions for this wallet"""
        from models.transaction import Transaction
        return Transaction.query.filter_by(wallet_id=self.id).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': float(self.balance),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
