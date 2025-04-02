import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-key-for-testing')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///local_service_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-key-for-testing')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # API
    API_TITLE = 'Local Service Platform API'
    API_VERSION = 'v1'
    SWAGGER = {
        'title': API_TITLE,
        'uiversion': 3,
        'specs_route': '/swagger/',
        'version': API_VERSION,
    }
