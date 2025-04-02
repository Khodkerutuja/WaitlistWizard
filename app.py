import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS

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
