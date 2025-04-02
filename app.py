import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flasgger import Swagger
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.Config')

# Set secret key
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
swagger = Swagger(app)
CORS(app)

# Import and register blueprints
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.wallet_controller import wallet_bp
from controllers.service_controller import service_bp
from controllers.booking_controller import booking_bp
from controllers.car_pool_controller import car_pool_bp
from controllers.gym_controller import gym_bp
from controllers.household_controller import household_bp
from controllers.mechanical_controller import mechanical_bp
from controllers.feedback_controller import feedback_bp
from controllers.admin_controller import admin_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
app.register_blueprint(service_bp, url_prefix='/api/services')
app.register_blueprint(booking_bp, url_prefix='/api/bookings')
app.register_blueprint(car_pool_bp, url_prefix='/api/carpool')
app.register_blueprint(gym_bp, url_prefix='/api/gym')
app.register_blueprint(household_bp, url_prefix='/api/household')
app.register_blueprint(mechanical_bp, url_prefix='/api/mechanical')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Import error handlers
from utils.error_handlers import *

# Create all database tables
with app.app_context():
    db.create_all()

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    responses:
      200:
        description: Application is healthy
    """
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'database': 'connected'
    }

# Home route
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    error = None
    
    if form.validate_on_submit():
        # Import here to avoid circular imports
        from models.user import User
        
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            # Store in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            session['jwt_token'] = access_token
            
            flash('Login successful!', 'success')
            return redirect(url_for('index', login='success'))
        else:
            error = 'Invalid email or password'
    
    return render_template('login.html', form=form, error=error)

# Registration page route
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm()
    error = None
    
    if form.validate_on_submit():
        # Import here to avoid circular imports
        from models.user import User
        from models.wallet import Wallet
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            error = 'Email address already exists'
        else:
            # Create new user
            new_user = User(
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_number=form.phone_number.data,
                role=form.role.data
            )
            
            # Additional fields
            new_user.address = form.address.data
            
            # Add service provider details if applicable
            if form.role.data == 'POWER_USER':
                new_user.service_type = form.service_type.data
                new_user.description = form.description.data
            
            # Save the user
            db.session.add(new_user)
            db.session.commit()
            
            # Create wallet for the user
            wallet = Wallet(user_id=new_user.id, initial_balance=0)
            db.session.add(wallet)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login_page', registered='success'))
    
    return render_template('register.html', form=form, error=error)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index', logout='success'))

# Service detail page
@app.route('/service/<int:service_id>')
def service_detail(service_id):
    # Import here to avoid circular imports
    from models.service import Service
    from models.user import User
    from models.feedback import Feedback
    from datetime import date
    
    service = Service.query.get_or_404(service_id)
    provider = User.query.get_or_404(service.provider_id)
    
    # Get reviews for this service
    reviews = Feedback.query.filter_by(service_id=service_id).all()
    
    # Calculate average rating
    avg_rating = None
    total_ratings = len(reviews)
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / len(reviews), 1)
    
    # Get today's date for the booking form
    today_date = date.today().isoformat()
    
    return render_template(
        'service_detail.html',
        service=service,
        provider=provider,
        reviews=reviews,
        avg_rating=avg_rating,
        total_ratings=total_ratings,
        today_date=today_date
    )

# Book service route
@app.route('/service/<int:service_id>/book', methods=['POST'])
def book_service(service_id):
    if not session.get('user_id'):
        flash('Please login to book a service.', 'danger')
        return redirect(url_for('login_page'))
    
    # Import here to avoid circular imports
    from models.service import Service
    from models.service import Booking
    from models.user import User
    
    service = Service.query.get_or_404(service_id)
    
    # Check if service is available
    if service.status != 'AVAILABLE':
        flash('This service is not available for booking.', 'danger')
        return redirect(url_for('service_detail', service_id=service_id))
    
    # Get form data
    booking_date = request.form.get('booking_date')
    notes = request.form.get('notes', '')
    
    # For car pool services, handle seat booking
    quantity = 1
    if service.service_type == 'CAR_POOL':
        num_seats = int(request.form.get('num_seats', 1))
        quantity = num_seats
        
        # Check if enough seats are available
        if num_seats > service.available_seats:
            flash(f'Only {service.available_seats} seats available.', 'danger')
            return redirect(url_for('service_detail', service_id=service_id))
        
        # Update available seats
        service.available_seats -= num_seats
    
    # Create booking
    booking = Booking(
        service_id=service_id,
        user_id=session['user_id'],
        booking_time=booking_date,
        amount=service.price,
        quantity=quantity,
        notes=notes,
        status='PENDING'
    )
    
    db.session.add(booking)
    db.session.commit()
    
    flash('Service booked successfully!', 'success')
    return redirect(url_for('service_detail', service_id=service_id))

# Add review route
@app.route('/service/<int:service_id>/review', methods=['POST'])
def add_review(service_id):
    if not session.get('user_id'):
        flash('Please login to add a review.', 'danger')
        return redirect(url_for('login_page'))
    
    # Import here to avoid circular imports
    from models.service import Service
    from models.feedback import Feedback
    
    service = Service.query.get_or_404(service_id)
    
    # Get form data
    rating = int(request.form.get('rating'))
    review_text = request.form.get('review')
    
    # Create feedback
    feedback = Feedback(
        user_id=session['user_id'],
        provider_id=service.provider_id,
        service_id=service_id,
        rating=rating,
        review=review_text
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    flash('Thank you for your review!', 'success')
    return redirect(url_for('service_detail', service_id=service_id))

# Services API for frontend
# My Bookings page
@app.route('/my-bookings')
def my_bookings():
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to view your bookings.', 'danger')
        return redirect(url_for('login_page'))
    
    return render_template('my_bookings.html')

@app.route('/wallet')
def wallet_page():
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to access your wallet.', 'danger')
        return redirect(url_for('login_page'))
    
    return render_template('wallet.html')

# Bookings API for frontend
@app.route('/bookings', methods=['GET'])
def get_bookings_ui():
    """Get bookings for the current user with optional status filter"""
    # Import here to avoid circular imports
    from models.booking import Booking
    from models.service import Service
    from models.user import User
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        user_role = session.get('user_role')
        status = request.args.get('status')
        
        # Determine query based on user role
        if user_role == 'POWER_USER':
            # For service providers, get bookings for their services
            query = (db.session.query(Booking)
                .join(Service, Booking.service_id == Service.id)
                .filter(Service.provider_id == user_id))
        else:
            # For regular users, get their bookings
            query = Booking.query.filter_by(user_id=user_id)
        
        # Apply status filter if provided
        if status:
            query = query.filter(Booking.status == status)
        
        # Get bookings and sort by created_at descending
        bookings = query.order_by(Booking.created_at.desc()).all()
        
        # Format response
        result = []
        for booking in bookings:
            service = Service.query.get(booking.service_id)
            
            booking_data = {
                'id': booking.id,
                'service_id': booking.service_id,
                'service_name': service.name if service else None,
                'status': booking.status,
                'amount': float(booking.amount) if booking.amount else 0,
                'quantity': booking.quantity,
                'notes': booking.notes,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': booking.updated_at.strftime('%Y-%m-%d %H:%M:%S') if booking.updated_at else None
            }
            
            # Add booking times if available
            if hasattr(booking, 'booking_time') and booking.booking_time:
                booking_data['booking_time'] = booking.booking_time.strftime('%Y-%m-%d %H:%M:%S')
            if hasattr(booking, 'start_time') and booking.start_time:
                booking_data['start_time'] = booking.start_time.strftime('%Y-%m-%d %H:%M:%S')
            if hasattr(booking, 'end_time') and booking.end_time:
                booking_data['end_time'] = booking.end_time.strftime('%Y-%m-%d %H:%M:%S')
                
            result.append(booking_data)
        
        return jsonify(result)
    except Exception as e:
        import logging
        logging.error(f"Error in get_bookings_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Booking actions
@app.route('/bookings/<int:booking_id>/payment', methods=['POST'])
def process_payment_ui(booking_id):
    """Process payment for a booking"""
    # Import here to avoid circular imports
    from services.booking_service import BookingService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        
        # Get the booking
        booking = BookingService.get_booking(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        # Check if it's the user's booking
        if booking.user_id != user_id:
            return jsonify({"error": "Not your booking"}), 403
        
        # Process payment
        success, message = BookingService.process_payment(booking_id)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
    except Exception as e:
        import logging
        logging.error(f"Error in process_payment_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking_ui(booking_id):
    """Cancel a booking"""
    # Import here to avoid circular imports
    from services.booking_service import BookingService
    from services.service_service import ServiceService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        user_role = session.get('user_role')
        
        # Get the booking
        booking = BookingService.get_booking(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        # Check if the user has access to this booking (consumer or provider can cancel)
        service = ServiceService.get_service(booking.service_id)
        
        if user_role != 'ADMIN':
            if service.provider_id != user_id and booking.user_id != user_id:
                return jsonify({"error": "Not your booking"}), 403
        
        # Cancel the booking
        success, message = BookingService.cancel_booking(booking_id)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
    except Exception as e:
        import logging
        logging.error(f"Error in cancel_booking_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/<int:booking_id>/confirm', methods=['POST'])
def confirm_booking_ui(booking_id):
    """Confirm a booking (provider only)"""
    # Import here to avoid circular imports
    from services.booking_service import BookingService
    from services.service_service import ServiceService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        user_role = session.get('user_role')
        
        if user_role != 'POWER_USER' and user_role != 'ADMIN':
            return jsonify({"error": "Only service providers can confirm bookings"}), 403
        
        # Get the booking
        booking = BookingService.get_booking(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        # Check if it's the provider's service
        service = ServiceService.get_service(booking.service_id)
        
        if service.provider_id != user_id and user_role != 'ADMIN':
            return jsonify({"error": "Not your service"}), 403
        
        # Confirm the booking
        success, message = BookingService.confirm_booking(booking_id)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        import logging
        logging.error(f"Error in confirm_booking_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/<int:booking_id>/reject', methods=['POST'])
def reject_booking_ui(booking_id):
    """Reject a booking (provider only)"""
    # Import here to avoid circular imports
    from services.booking_service import BookingService
    from services.service_service import ServiceService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        user_role = session.get('user_role')
        
        if user_role != 'POWER_USER' and user_role != 'ADMIN':
            return jsonify({"error": "Only service providers can reject bookings"}), 403
        
        # Get the booking
        booking = BookingService.get_booking(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        # Check if it's the provider's service
        service = ServiceService.get_service(booking.service_id)
        
        if service.provider_id != user_id and user_role != 'ADMIN':
            return jsonify({"error": "Not your service"}), 403
        
        # Get reason from request body
        data = request.get_json(silent=True) or {}
        reason = data.get('reason')
        
        # Reject the booking
        success, message = BookingService.reject_booking(booking_id, reason)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        import logging
        logging.error(f"Error in reject_booking_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/<int:booking_id>/complete', methods=['POST'])
def complete_booking_ui(booking_id):
    """Mark a booking as completed (provider only)"""
    # Import here to avoid circular imports
    from services.booking_service import BookingService
    from services.service_service import ServiceService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        user_role = session.get('user_role')
        
        if user_role != 'POWER_USER' and user_role != 'ADMIN':
            return jsonify({"error": "Only service providers can complete bookings"}), 403
        
        # Get the booking
        booking = BookingService.get_booking(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        # Check if it's the provider's service
        service = ServiceService.get_service(booking.service_id)
        if not service:
            return jsonify({"error": "Service not found"}), 404
        
        if user_role != 'ADMIN' and service.provider_id != user_id:
            return jsonify({"error": "Not your service"}), 403
        
        # Mark booking as completed
        success, message = BookingService.complete_booking(booking_id)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
    except Exception as e:
        import logging
        logging.error(f"Error in complete_booking_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Wallet API for UI
@app.route('/api/wallet', methods=['GET'])
def get_wallet_ui():
    """Get wallet for the current user"""
    # Import here to avoid circular imports
    from services.wallet_service import WalletService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        
        # Get the wallet
        wallet = WalletService.get_wallet(user_id)
        if not wallet:
            return jsonify({"error": "Wallet not found"}), 404
        
        # Format response
        wallet_data = wallet.to_dict()
        
        # Get recent transactions
        transactions = WalletService.get_transactions(wallet.id, 5)
        
        return jsonify({
            "wallet": wallet_data,
            "recent_transactions": [tx.to_dict() for tx in transactions]
        }), 200
    except Exception as e:
        import logging
        logging.error(f"Error in get_wallet_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/transactions', methods=['GET'])
def get_wallet_transactions_ui():
    """Get transactions for the current user's wallet"""
    # Import here to avoid circular imports
    from services.wallet_service import WalletService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        
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
    except Exception as e:
        import logging
        logging.error(f"Error in get_wallet_transactions_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/add-funds', methods=['POST'])
def add_funds_ui():
    """Add funds to user's wallet"""
    # Import here to avoid circular imports
    from services.wallet_service import WalletService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session['user_id']
        
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
                "message": f"₹{amount:.2f} added to wallet successfully",
                "wallet": wallet.to_dict()
            }), 200
        else:
            return jsonify({"error": result}), 400
    except Exception as e:
        import logging
        logging.error(f"Error in add_funds_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/transfer', methods=['POST'])
def transfer_funds_ui():
    """Transfer funds to another user"""
    # Import here to avoid circular imports
    from services.wallet_service import WalletService
    
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        from_user_id = session['user_id']
        
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
    except Exception as e:
        import logging
        logging.error(f"Error in transfer_funds_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/services-ui', methods=['GET'])
def get_services_ui():
    """Get services for UI display with filtering options"""
    # Import here to avoid circular imports
    from models.service import Service
    from models.user import User
    from datetime import datetime
    import logging
    
    try:
        # Get query parameters
        service_type = request.args.get('service_type')
        status = request.args.get('status', 'AVAILABLE')
        
        # Build query
        query = Service.query.filter_by(status=status)
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        # Get services
        services = query.all()
        
        # Format response
        result = []
        for service in services:
            try:
                provider = User.query.get(service.provider_id)
                provider_name = f"{provider.first_name} {provider.last_name}" if provider else "Unknown"
                
                service_data = {
                    'id': service.id,
                    'name': service.name,
                    'description': service.description,
                    'service_type': service.service_type,
                    'price': float(service.price),
                    'status': service.status,
                    'provider_id': service.provider_id,
                    'provider_name': provider_name,
                    'created_at': service.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Add location from base class for all services
                if hasattr(service, 'location') and service.location:
                    service_data['location'] = service.location
                
                # Add service type specific fields based on what values are available
                # We're not using getattr to avoid the deferred loader issues
                if service.service_type == 'CAR_POOL':
                    # Only add existing attributes to avoid accessing deferred loaders 
                    # that don't have values set yet
                    car_pool_fields = {}
                    
                    # Only include fields that actually exist on the service instance
                    # to prevent deferred loader errors
                    if hasattr(service, '__dict__'):
                        service_dict = service.__dict__
                        
                        for field in ['source', 'destination', 'vehicle_type', 'vehicle_model', 'vehicle_number']:
                            if field in service_dict:
                                car_pool_fields[field] = service_dict[field]
                        
                        if 'departure_time' in service_dict:
                            if isinstance(service_dict['departure_time'], datetime):
                                car_pool_fields['departure_time'] = service_dict['departure_time'].strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                car_pool_fields['departure_time'] = service_dict['departure_time']
                        
                        if 'available_seats' in service_dict:
                            car_pool_fields['available_seats'] = service_dict['available_seats']
                        
                        if 'total_seats' in service_dict:
                            car_pool_fields['total_seats'] = service_dict['total_seats']
                    
                    service_data.update(car_pool_fields)
                elif service.service_type == 'GYM_FITNESS':
                    gym_fields = {}
                    
                    if hasattr(service, '__dict__'):
                        service_dict = service.__dict__
                        
                        for field in ['operating_hours', 'trainer_experience', 'category']:
                            if field in service_dict:
                                gym_fields[field] = service_dict[field]
                    
                    service_data.update(gym_fields)
                elif service.service_type == 'HOUSEHOLD':
                    household_fields = {}
                    
                    if hasattr(service, '__dict__'):
                        service_dict = service.__dict__
                        
                        for field in ['category', 'estimated_time', 'experience', 'service_area']:
                            if field in service_dict:
                                household_fields[field] = service_dict[field]
                    
                    service_data.update(household_fields)
                elif service.service_type == 'MECHANICAL':
                    mechanical_fields = {}
                    
                    if hasattr(service, '__dict__'):
                        service_dict = service.__dict__
                        
                        for field in ['specialization', 'vehicle_types', 'experience', 'workshop_location']:
                            if field in service_dict:
                                mechanical_fields[field] = service_dict[field]
                    
                    service_data.update(mechanical_fields)
                
                result.append(service_data)
            except Exception as e:
                # Log error but continue processing other services
                logging.error(f"Error processing service {service.id}: {str(e)}")
                continue
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in get_services_ui: {str(e)}")
        return jsonify({"error": str(e)}), 500
