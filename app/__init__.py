import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name="development"):
    app = Flask(__name__)
    
    # Basic configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # API configuration
    app.config["API_TITLE"] = "Learning Platform API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    api = Api(app)
    
    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = "my-super-secret-key-123"  # Development only
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Debug endpoint to verify JWT configuration
    @app.route('/api/test-jwt')
    @jwt_required()
    def test_jwt():
        current_user = get_jwt_identity()
        return jsonify({"message": "JWT working", "user_id": current_user})
    
    # Register blueprints
    from app.api.users import blp as users_blp
    from app.api.auth import blp as auth_blp
    api.register_blueprint(users_blp, url_prefix="/api/users")
    api.register_blueprint(auth_blp, url_prefix="/api/auth")
    
    return app

# Create an application instance for 'flask run'
app = create_app(os.getenv('FLASK_CONFIG', 'default'))

