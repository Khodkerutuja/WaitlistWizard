from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.wallet_service import WalletService
from schemas.wallet_schema import wallet_schema, wallet_deposit_schema, transactions_schema
from utils.auth_utils import active_user_required
from utils.validation import validate_positive_amount
from flasgger import swag_from

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Wallet'],
    'summary': 'Get wallet',
    'description': 'Get current user wallet information',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        }
    ],
    'responses': {
        '200': {
            'description': 'Wallet information'
        },
        '404': {
            'description': 'Wallet not found'
        }
    }
})
def get_wallet():
    user_id = get_jwt_identity()
    wallet = WalletService.get_wallet(user_id)
    
    if not wallet:
        return jsonify(message="Wallet not found"), 404
    
    result = wallet_schema.dump(wallet)
    return jsonify(wallet=result), 200

@wallet_bp.route('/deposit', methods=['POST'])
@jwt_required()
@active_user_required()
@swag_from({
    'tags': ['Wallet'],
    'summary': 'Deposit funds',
    'description': 'Add funds to current user wallet',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'amount': {'type': 'number', 'minimum': 0.01}
                },
                'required': ['amount']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Funds deposited successfully'
        },
        '400': {
            'description': 'Invalid input data'
        },
        '404': {
            'description': 'Wallet not found'
        }
    }
})
def deposit_funds():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify(message="No input data provided"), 400
    
    # Validate with schema
    errors = wallet_deposit_schema.validate(data)
    if errors:
        return jsonify(errors=errors), 400
    
    amount = data.get('amount')
    
    # Deposit funds
    result, message = WalletService.deposit_funds(user_id, amount)
    if not result:
        return jsonify(message=message), 400
    
    return jsonify(message=message, transaction=result), 200

@wallet_bp.route('/transactions', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Wallet'],
    'summary': 'Get transaction history',
    'description': 'Get current user wallet transaction history',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT token'
        },
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Maximum number of transactions to return (default: 5)'
        }
    ],
    'responses': {
        '200': {
            'description': 'Transaction history'
        },
        '404': {
            'description': 'Wallet not found'
        }
    }
})
def get_transactions():
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 5, type=int)
    
    transactions, message = WalletService.get_transaction_history(user_id, limit)
    
    if not transactions and message == "Wallet not found":
        return jsonify(message=message), 404
    
    result = transactions_schema.dump(transactions)
    return jsonify(transactions=result), 200
