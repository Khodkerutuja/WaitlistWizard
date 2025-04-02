from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.wallet_service import WalletService
from utils.jwt_manager import admin_required

wallet_bp = Blueprint('wallet', __name__)
wallet_service = WalletService()

@wallet_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_wallet_balance():
    """
    Get current user's wallet balance
    ---
    tags:
      - Wallet
    security:
      - JWT: []
    responses:
      200:
        description: Wallet balance
      401:
        description: Unauthorized
      404:
        description: Wallet not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    try:
        wallet = wallet_service.get_wallet_by_user_id(user_id)
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404
        
        return jsonify(wallet.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallet_bp.route('/deposit', methods=['POST'])
@jwt_required()
def deposit_to_wallet():
    """
    Add money to current user's wallet
    ---
    tags:
      - Wallet
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - amount
          properties:
            amount:
              type: number
              minimum: 1
            description:
              type: string
    responses:
      200:
        description: Money added to wallet successfully
      400:
        description: Invalid amount
      401:
        description: Unauthorized
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    data = request.get_json()
    
    # Validate amount
    if 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount format'}), 400
    
    description = data.get('description', 'Wallet deposit')
    
    try:
        wallet, transaction = wallet_service.deposit_to_wallet(
            user_id=user_id,
            amount=amount,
            description=description
        )
        return jsonify({
            'message': 'Money added to wallet successfully',
            'wallet': wallet.to_dict(),
            'transaction': transaction.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallet_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transaction_history():
    """
    Get transaction history for current user's wallet
    ---
    tags:
      - Wallet
    security:
      - JWT: []
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 5
        description: Number of transactions to return
    responses:
      200:
        description: Transaction history
      401:
        description: Unauthorized
      404:
        description: Wallet not found
    """
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    try:
        limit = request.args.get('limit', 5, type=int)
        transactions = wallet_service.get_transaction_history(user_id, limit)
        
        return jsonify([transaction.to_dict() for transaction in transactions]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallet_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user_wallet(user_id):
    """
    Get wallet for a specific user (Admin only)
    ---
    tags:
      - Wallet
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User's wallet
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Wallet not found
    """
    try:
        wallet = wallet_service.get_wallet_by_user_id(user_id)
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404
        
        return jsonify(wallet.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallet_bp.route('/user/<int:user_id>/transactions', methods=['GET'])
@jwt_required()
@admin_required
def get_user_transactions(user_id):
    """
    Get transaction history for a specific user (Admin only)
    ---
    tags:
      - Wallet
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID
      - name: limit
        in: query
        type: integer
        required: false
        default: 5
        description: Number of transactions to return
    responses:
      200:
        description: User's transaction history
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Wallet not found
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        transactions = wallet_service.get_transaction_history(user_id, limit)
        
        return jsonify([transaction.to_dict() for transaction in transactions]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallet_bp.route('/admin/adjust', methods=['POST'])
@jwt_required()
@admin_required
def admin_adjust_wallet():
    """
    Admin adjustment to a user's wallet
    ---
    tags:
      - Wallet
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - amount
            - description
          properties:
            user_id:
              type: integer
            amount:
              type: number
            description:
              type: string
    responses:
      200:
        description: Wallet adjusted successfully
      400:
        description: Invalid input
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: User not found
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['user_id', 'amount', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        user_id = int(data['user_id'])
        amount = float(data['amount'])
        description = data['description']
        
        wallet, transaction = wallet_service.admin_adjust_wallet(
            user_id=user_id,
            amount=amount,
            description=description
        )
        
        return jsonify({
            'message': 'Wallet adjusted successfully',
            'wallet': wallet.to_dict(),
            'transaction': transaction.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
