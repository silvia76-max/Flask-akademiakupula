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
    logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')} = 'sqlite:///akademiakupula.db'")

    # Configure middleware for handling proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Configure CORS
    logger.info("Configuring CORS")
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
            "expose_headers": ["Content-Length", "X-Process-Time"],
            "supports_credentials": True,
            "max_age": 86400  # 24 horas
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

    # Configurar JWT para convertir el ID a string
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        # Convertir el ID a string para evitar el error "Subject must be a string"
        return str(user_id)

    # Configurar JWT para cargar el usuario desde la base de datos
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        # Obtener el ID del usuario desde el token
        identity = jwt_data["sub"]
        # Convertir a entero si es necesario
        user_id = int(identity) if isinstance(identity, str) else identity
        # Buscar el usuario en la base de datos
        from app.models.user import User
        return User.query.filter_by(id=user_id).one_or_none()

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

    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def add_headers(response):
        # Add processing time header
        if hasattr(request, 'start_time'):
            process_time = time.time() - request.start_time
            response.headers['X-Process-Time'] = f"{process_time:.4f}s"

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN' 
        response.headers['X-XSS-Protection'] = '1; mode=block'

        return response

    # Register models
    logger.info("Registering models")
    from app.models import register_models
    models = register_models()

    # Register blueprints
    logger.info("Registering blueprints")
    from app.routes.auth_routes import auth
    from app.routes.admin_courses import admin_courses_bp
    from app.routes.cursos import cursos_bp
    from app.routes.test_routes import test_bp
    from app.routes.contacto_routes import contacto_bp
    from app.routes.user_courses import user_courses_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.session_routes import sessions_bp

    # Intentar importar rutas de pago si existen
    try:
        from app.routes.payment_routes import payment_bp
        has_payment_routes = True
    except ImportError:
        has_payment_routes = False
        logger.warning("No se pudieron importar las rutas de pago")

    app.register_blueprint(admin_courses_bp, url_prefix='/api/admin_courses')
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(contacto_bp, url_prefix='/api/contacto')
    app.register_blueprint(user_courses_bp, url_prefix='/api/user')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')

    # Registrar rutas de pago si existen
    if has_payment_routes:
        app.register_blueprint(payment_bp, url_prefix='/api/payment')

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
