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
        from models.user_model import User
        
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            # Store in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            session['jwt_token'] = access_token
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
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
        from models.user_model import User
        from models.wallet_model import Wallet
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            error = 'Email address already exists'
        else:
            # Create new user
            new_user = User(
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_number=form.phone_number.data,
                address=form.address.data,
                role=form.role.data,
                status='ACTIVE'
            )
            
            # Add service provider details if applicable
            if form.role.data == 'POWER_USER':
                new_user.service_type = form.service_type.data
                new_user.description = form.description.data
            
            # Save the user
            db.session.add(new_user)
            db.session.commit()
            
            # Create wallet for the user
            wallet = Wallet(user_id=new_user.id, balance=0)
            db.session.add(wallet)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login_page'))
    
    return render_template('register.html', form=form, error=error)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Service detail page
@app.route('/service/<int:service_id>')
def service_detail(service_id):
    # Import here to avoid circular imports
    from models.service_model import Service
    from models.user_model import User
    from models.feedback_model import Feedback
    
    service = Service.query.get_or_404(service_id)
    provider = User.query.get_or_404(service.provider_id)
    
    # Get reviews for this service
    reviews = Feedback.query.filter_by(service_id=service_id).all()
    
    # Calculate average rating
    avg_rating = None
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / len(reviews), 1)
    
    return render_template(
        'service_detail.html',
        service=service,
        provider=provider,
        reviews=reviews,
        avg_rating=avg_rating,
        total_ratings=len(reviews)
    )

# Book service route
@app.route('/service/<int:service_id>/book', methods=['POST'])
def book_service(service_id):
    if not session.get('user_id'):
        flash('Please login to book a service.', 'danger')
        return redirect(url_for('login_page'))
    
    # Import here to avoid circular imports
    from models.service_model import Service
    from models.booking_model import Booking
    from models.user_model import User
    
    service = Service.query.get_or_404(service_id)
    
    # Check if service is available
    if service.status != 'AVAILABLE':
        flash('This service is not available for booking.', 'danger')
        return redirect(url_for('service_detail', service_id=service_id))
    
    # Get form data
    booking_date = request.form.get('booking_date')
    
    # For car pool services, handle seat booking
    if service.service_type == 'CAR_POOL':
        num_seats = int(request.form.get('num_seats', 1))
        
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
        booking_date=booking_date,
        status='CONFIRMED',
        amount=service.price
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
    from models.service_model import Service
    from models.feedback_model import Feedback
    
    service = Service.query.get_or_404(service_id)
    
    # Get form data
    rating = int(request.form.get('rating'))
    review_text = request.form.get('review')
    
    # Create feedback
    feedback = Feedback(
        service_id=service_id,
        user_id=session['user_id'],
        rating=rating,
        review=review_text
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    flash('Thank you for your review!', 'success')
    return redirect(url_for('service_detail', service_id=service_id))

# Services API for frontend
@app.route('/api/services-ui', methods=['GET'])
def get_services_ui():
    """Get services for UI display with filtering options"""
    # Import here to avoid circular imports
    from models.service_model import Service
    from models.user_model import User
    
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
        provider = User.query.get(service.provider_id)
        provider_name = f"{provider.first_name} {provider.last_name}" if provider else "Unknown"
        
        service_data = {
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'service_type': service.service_type,
            'price': service.price,
            'status': service.status,
            'provider_id': service.provider_id,
            'provider_name': provider_name,
            'created_at': service.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add service type specific fields
        if service.service_type == 'CAR_POOL':
            service_data.update({
                'source': getattr(service, 'source', None),
                'destination': getattr(service, 'destination', None),
                'departure_time': getattr(service, 'departure_time', None),
                'available_seats': getattr(service, 'available_seats', 0),
                'total_seats': getattr(service, 'total_seats', 0),
                'vehicle_type': getattr(service, 'vehicle_type', None),
                'vehicle_model': getattr(service, 'vehicle_model', None),
                'vehicle_number': getattr(service, 'vehicle_number', None),
            })
        elif service.service_type == 'GYM_FITNESS':
            service_data.update({
                'location': getattr(service, 'location', None),
                'operating_hours': getattr(service, 'operating_hours', None),
                'trainer_experience': getattr(service, 'trainer_experience', 0),
                'category': getattr(service, 'category', None),
            })
        elif service.service_type == 'HOUSEHOLD':
            service_data.update({
                'category': getattr(service, 'category', None),
                'estimated_time': getattr(service, 'estimated_time', 0),
                'experience': getattr(service, 'experience', 0),
                'service_area': getattr(service, 'service_area', None),
            })
        elif service.service_type == 'MECHANICAL':
            service_data.update({
                'specialization': getattr(service, 'specialization', None),
                'vehicle_types': getattr(service, 'vehicle_types', None),
                'experience': getattr(service, 'experience', 0),
                'workshop_location': getattr(service, 'workshop_location', None),
            })
        
        result.append(service_data)
    
    return jsonify(result)
