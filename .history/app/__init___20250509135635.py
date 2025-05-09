from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import logging

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file into environment variables

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
db = SQLAlchemy()
mail = Mail()


def create_app():
    logger.info("Creating Flask application")
    app = Flask(__name__)


    # Basic configuration
    logger.info("Loading application configuration")
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///akademiakupula.db'
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key'  # Use the same key everywhere
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or 'another-key'
    app.config.update(
        SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )
    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })


    logger.info("Initializing extensions")
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)


    from app.routes.auth_routes import auth
    from app.routes.cursos import cursos_bp
    from app.routes.test_routes import test_bp
    from app.routes.contacto_routes import contacto_bp

    # Register blueprints
    logger.info("Registering blueprints")
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(contacto_bp, url_prefix='/api/contacto')

    # Set up error handlers
    logger.info("Setting up error handlers")

    # Define a function to create standardized error responses
    def make_error_response(message, status_code):
        return jsonify({
            "success": False,
            "message": message,
            "data": None
        }), status_code

    # Register error handlers
    @app.errorhandler(404)
    def handle_not_found_error(error):
        logger.warning(f"404 error: {error}")
        return make_error_response("Resource not found", 404)

    @app.errorhandler(500)
    def handle_server_error(error):
        logger.error(f"500 error: {error}")
        return make_error_response("Internal server error", 500)

    logger.info("Flask application created successfully")
    return app
