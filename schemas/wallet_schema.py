from marshmallow import Schema, fields, validate

class WalletSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    balance = fields.Decimal(as_string=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class TransactionSchema(Schema):
    id = fields.Integer(dump_only=True)
    wallet_id = fields.Integer(dump_only=True)
    amount = fields.Decimal(as_string=True, dump_only=True)
    transaction_type = fields.String(dump_only=True)
    description = fields.String(dump_only=True)
    reference_id = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class WalletDepositSchema(Schema):
    amount = fields.Decimal(as_string=True, required=True, validate=validate.Range(min=1))
    description = fields.String()

class AdminWalletAdjustmentSchema(Schema):
    user_id = fields.Integer(required=True)
    amount = fields.Decimal(as_string=True, required=True)
    description = fields.String(required=True)
