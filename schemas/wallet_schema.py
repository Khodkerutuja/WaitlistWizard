from marshmallow import fields, validate
from app import ma
from models import Wallet, Transaction, TransactionType

class TransactionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Transaction
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    wallet_id = ma.auto_field(dump_only=True)
    amount = ma.auto_field(required=True, validate=validate.Range(min=0.01))
    transaction_type = fields.Enum(TransactionType, by_value=True, dump_only=True)
    description = ma.auto_field()
    reference_id = ma.auto_field()
    created_at = ma.auto_field(dump_only=True)

class WalletSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Wallet
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    balance = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    # Include latest transactions
    transactions = fields.Nested(TransactionSchema, many=True, dump_only=True)

class WalletDepositSchema(ma.Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))

# Initialize schemas
wallet_schema = WalletSchema()
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
wallet_deposit_schema = WalletDepositSchema()
