import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from app.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name="development"):
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:*",
                "http://127.0.0.1:*",
                "https://localhost:*",
                "https://127.0.0.1:*"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Load the config
    app.config.from_object(config[config_name])
    
    # Set API configuration if not in config
    if "API_TITLE" not in app.config:
        app.config["API_TITLE"] = "Student Portal API"
        app.config["API_VERSION"] = "v1"
        app.config["OPENAPI_VERSION"] = "3.0.2"
        app.config["OPENAPI_URL_PREFIX"] = "/"
        app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
        app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Initialize API after setting configuration
    api = Api(app)
    
    # Debug endpoint to verify JWT configuration
    @app.route('/api/test-jwt')
    @jwt_required()
    def test_jwt():
        current_user = get_jwt_identity()
        return jsonify({"message": "JWT working", "user_id": current_user})
    
    # Register blueprints
    from app.api.users import blp as users_blp
    from app.api.auth import blp as auth_blp
    from app.api.courses import blp as courses_blp
    from app.api.classes import blp as classes_blueprint
    
    api.register_blueprint(users_blp, url_prefix="/api/users")
    api.register_blueprint(auth_blp, url_prefix="/api/auth")
    api.register_blueprint(courses_blp, url_prefix="/api/courses")
    api.register_blueprint(classes_blueprint, url_prefix='/api/classes')
    
    return app

# Only create the app instance if running directly (not for testing)
if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))



