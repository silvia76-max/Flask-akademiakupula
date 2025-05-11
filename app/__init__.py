from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_compress import Compress
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
import time
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('FLASK_DEBUG', 'True') == 'True' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()
compress = Compress()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    """Create and configure the Flask application"""
    logger.info("Creating Flask application")
    app = Flask(__name__)

    # Load configuration
    logger.info("Loading application configuration")
    app.config.from_object('config.Config')

    # Log important configuration values for debugging
    logger.info(f"Environment: {app.config.get('ENV')}")
    logger.info(f"Debug mode: {app.config.get('DEBUG')}")
    logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # Configure middleware for handling proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Configure CORS
    logger.info("Configuring CORS")
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Initialize extensions
    logger.info("Initializing extensions")

    # Database
    db.init_app(app)
    logger.info("SQLAlchemy initialized")

    # Security
    bcrypt.init_app(app)
    logger.info("Bcrypt initialized")

    jwt.init_app(app)
    logger.info("JWT initialized")

    # Database migrations
    migrate.init_app(app, db)
    logger.info("Migrate initialized")

    # Email
    mail.init_app(app)
    logger.info("Mail initialized")

    # Performance optimizations
    compress.init_app(app)
    logger.info("Compress initialized")

    cache.init_app(app)
    logger.info("Cache initialized")

    # Rate limiting
    limiter.init_app(app)
    logger.info("Rate limiter initialized")

    # Create database tables if they don't exist
    with app.app_context():
        try:
            logger.info("Creating database tables if they don't exist")
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")

    # Request processing time middleware
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        # Add processing time header
        if hasattr(request, 'start_time'):
            process_time = time.time() - request.start_time
            response.headers['X-Process-Time'] = f"{process_time:.4f}s"

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        return response

    # Register models
    logger.info("Registering models")
    from app.models import register_models
    models = register_models()

    # Register blueprints
    logger.info("Registering blueprints")
    from app.routes.auth_routes import auth
    from app.routes.cursos import cursos_bp
    from app.routes.test_routes import test_bp
    from app.routes.contacto_routes import contacto_bp
    from app.routes.user_courses import user_courses_bp

    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(contacto_bp, url_prefix='/api/contacto')
    app.register_blueprint(user_courses_bp, url_prefix='/api/user')

    # Set up error handlers
    logger.info("Setting up error handlers")

    # Define a function to create standardized error responses
    def make_error_response(message, status_code, errors=None):
        """Create a standardized JSON error response"""
        response = {
            "success": False,
            "message": message,
            "data": None
        }
        if errors:
            response["errors"] = errors
        return jsonify(response), status_code

    # Register error handlers
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"400 error: {error}")
        return make_error_response("Solicitud incorrecta", 400)

    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized errors"""
        logger.warning(f"401 error: {error}")
        return make_error_response("No autorizado", 401)

    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden errors"""
        logger.warning(f"403 error: {error}")
        return make_error_response("Acceso prohibido", 403)

    @app.errorhandler(404)
    def handle_not_found_error(error):
        """Handle 404 Not Found errors"""
        logger.warning(f"404 error: {error}")
        return make_error_response("Recurso no encontrado", 404)

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        logger.warning(f"405 error: {error}")
        return make_error_response("Método no permitido", 405)

    @app.errorhandler(429)
    def handle_too_many_requests(error):
        """Handle 429 Too Many Requests errors"""
        logger.warning(f"429 error: {error}")
        return make_error_response("Demasiadas solicitudes. Por favor, inténtalo más tarde.", 429)

    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"500 error: {error}")
        return make_error_response("Error interno del servidor", 500)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error):
        """Handle any unhandled exception"""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        return make_error_response("Error interno del servidor", 500)

    logger.info("Flask application created successfully")
    return app
