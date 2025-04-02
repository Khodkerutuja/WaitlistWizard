import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
ma = Marshmallow()
jwt = JWTManager()
swagger = Swagger()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-key-for-testing")
    
    # Initialize extensions with app
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.users import users_bp
    from routes.wallet import wallet_bp
    from routes.services import services_bp
    from routes.car_pool import car_pool_bp
    from routes.gym import gym_bp
    from routes.household import household_bp
    from routes.mechanical import mechanical_bp
    from routes.feedback import feedback_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(car_pool_bp, url_prefix='/api/car-pool')
    app.register_blueprint(gym_bp, url_prefix='/api/gym')
    app.register_blueprint(household_bp, url_prefix='/api/household')
    app.register_blueprint(mechanical_bp, url_prefix='/api/mechanical')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'up',
            'version': app.config['API_VERSION'],
            'database': 'connected' if db.engine.pool.checkin() else 'disconnected'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Internal server error'}, 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
