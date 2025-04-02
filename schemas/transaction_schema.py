from marshmallow import Schema, fields
from models.wallet import TransactionType

class TransactionSchema(Schema):
    id = fields.Integer(dump_only=True)
    wallet_id = fields.Integer(dump_only=True)
    amount = fields.Decimal(as_string=True, dump_only=True)
    transaction_type = fields.String(dump_only=True, validate=fields.validate.OneOf([
        TransactionType.DEPOSIT, TransactionType.WITHDRAWAL, TransactionType.PAYMENT,
        TransactionType.REFUND, TransactionType.COMMISSION, TransactionType.ADMIN_ADJUSTMENT
    ]))
    description = fields.String(dump_only=True)
    reference_id = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    # Include additional details
    user = fields.Method('get_user', dump_only=True)
    
    def get_user(self, obj):
        from models.wallet import Wallet
        from models.user import User
        
        wallet = Wallet.query.get(obj.wallet_id)
        if wallet:
            user = User.query.get(wallet.user_id)
            if user:
                return {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email
                }
        return None
