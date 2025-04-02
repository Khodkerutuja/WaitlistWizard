from flask import Blueprint, request, jsonify
from flask_login import current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from services.wallet_service import WalletService
from models.user import UserRole
from utils.auth_utils import admin_required

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/', methods=['GET'])
@jwt_required()
def get_wallet():
    """
    Get wallet for the current user
    ---
    tags:
      - Wallet
    security:
      - JWT: []
    responses:
      200:
        description: Wallet details
      401:
        description: Unauthorized
      404:
        description: Wallet not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get the wallet
    wallet = WalletService.get_wallet(user_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    
    # Format response
    wallet_data = wallet.to_dict()
    
    # Get recent transactions
    transactions = WalletService.get_transactions(wallet.id)
    
    return jsonify({
        "wallet": wallet_data,
        "recent_transactions": [tx.to_dict() for tx in transactions]
    }), 200

@wallet_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """
    Get wallet transactions for the current user
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
        default: 10
        description: Maximum number of transactions to return
    responses:
      200:
        description: List of transactions
      401:
        description: Unauthorized
      404:
        description: Wallet not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get the wallet
    wallet = WalletService.get_wallet(user_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    
    # Get limit from query parameters
    limit = int(request.args.get('limit', 10))
    
    # Get transactions
    transactions = WalletService.get_transactions(wallet.id, limit)
    
    return jsonify({
        "transactions": [tx.to_dict() for tx in transactions]
    }), 200

@wallet_bp.route('/add-funds', methods=['POST'])
@jwt_required()
def add_funds():
    """
    Add funds to user wallet
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
              format: float
              minimum: 0.01
    responses:
      200:
        description: Funds added successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      404:
        description: Wallet not found
    """
    # Get the current user id from the JWT token
    user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({"error": "amount is required"}), 400
    
    try:
        amount = float(data.get('amount'))
    except (ValueError, TypeError):
        return jsonify({"error": "amount must be a number"}), 400
    
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400
    
    # Add funds to wallet
    success, result = WalletService.add_funds(user_id, amount)
    
    if success:
        wallet = result
        return jsonify({
            "message": f"${amount:.2f} added to wallet successfully",
            "wallet": wallet.to_dict()
        }), 200
    else:
        return jsonify({"error": result}), 400

@wallet_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_funds():
    """
    Transfer funds to another user
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
            - to_user_id
            - amount
          properties:
            to_user_id:
              type: integer
            amount:
              type: number
              format: float
              minimum: 0.01
            description:
              type: string
    responses:
      200:
        description: Funds transferred successfully
      400:
        description: Invalid input data or insufficient funds
      401:
        description: Unauthorized
      404:
        description: Wallet not found
    """
    # Get the current user id from the JWT token
    from_user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    if not data or 'to_user_id' not in data or 'amount' not in data:
        return jsonify({"error": "to_user_id and amount are required"}), 400
    
    try:
        to_user_id = int(data.get('to_user_id'))
        amount = float(data.get('amount'))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input types"}), 400
    
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400
    
    if from_user_id == to_user_id:
        return jsonify({"error": "Cannot transfer to yourself"}), 400
    
    # Get the optional description
    description = data.get('description')
    
    # Transfer funds
    success, message = WalletService.transfer_funds(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        amount=amount,
        description=description
    )
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@wallet_bp.route('/admin/balance', methods=['POST'])
@jwt_required()
@admin_required
def admin_adjust_balance():
    """
    Adjust user wallet balance (admin only)
    ---
    tags:
      - Wallet
      - Admin
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
          properties:
            user_id:
              type: integer
            amount:
              type: number
              format: float
            description:
              type: string
    responses:
      200:
        description: Balance adjusted successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Wallet not found
    """
    # Get request data
    data = request.get_json()
    if not data or 'user_id' not in data or 'amount' not in data:
        return jsonify({"error": "user_id and amount are required"}), 400
    
    try:
        user_id = int(data.get('user_id'))
        amount = float(data.get('amount'))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input types"}), 400
    
    # Get the optional description
    description = data.get('description')
    
    # Adjust balance
    success, result = WalletService.adjust_balance(
        user_id=user_id,
        amount=amount,
        description=description
    )
    
    if success:
        wallet = result
        return jsonify({
            "message": f"Wallet balance adjusted successfully",
            "wallet": wallet.to_dict()
        }), 200
    else:
        return jsonify({"error": result}), 400

@wallet_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_user_wallet(user_id):
    """
    Get user wallet (admin only)
    ---
    tags:
      - Wallet
      - Admin
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
        description: Wallet details
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Wallet not found
    """
    # Get the wallet
    wallet = WalletService.get_wallet(user_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    
    # Get transactions
    transactions = WalletService.get_transactions(wallet.id, 20)
    
    return jsonify({
        "wallet": wallet.to_dict(),
        "transactions": [tx.to_dict() for tx in transactions]
    }), 200

@wallet_bp.route('/admin/create', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_wallet():
    """
    Create a new wallet for a user (admin only)
    ---
    tags:
      - Wallet
      - Admin
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
          properties:
            user_id:
              type: integer
            initial_balance:
              type: number
              format: float
              default: 0
    responses:
      201:
        description: Wallet created successfully
      400:
        description: Invalid input data or wallet already exists
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    # Get request data
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        user_id = int(data.get('user_id'))
        initial_balance = float(data.get('initial_balance', 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input types"}), 400
    
    # Create wallet
    success, result = WalletService.create_wallet(
        user_id=user_id,
        initial_balance=initial_balance
    )
    
    if success:
        wallet = result
        return jsonify({
            "message": "Wallet created successfully",
            "wallet": wallet.to_dict()
        }), 201
    else:
        return jsonify({"error": result}), 400