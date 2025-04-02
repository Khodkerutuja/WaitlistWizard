from datetime import datetime
from app import db
from models.enum_types import TransactionType

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(db.String(50), nullable=True)  # For linking to services or other entities
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, wallet_id, amount, transaction_type, description=None, reference_id=None):
        self.wallet_id = wallet_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.reference_id = reference_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type,
            'description': self.description,
            'reference_id': self.reference_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
