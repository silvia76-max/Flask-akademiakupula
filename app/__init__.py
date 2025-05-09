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
from dotenv import load_dotenv  # Use the official python-dotenv package
load_dotenv()  # This loads the .env file into environment variables

# Basic logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Cambiado a DEBUG para ver más información
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask extensions - Creamos una única instancia de cada extensión
# Estas instancias se compartirán en toda la aplicación
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()


def create_app():
    logger.info("Creating Flask application")
    app = Flask(__name__)

    # Basic configuration
    logger.info("Loading application configuration")
    app.config.from_object('config.Config')

    # Configurar la URI de la base de datos explícitamente
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///akademiakupula.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurar claves secretas
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key'
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or 'another-key'

    # Imprimir la configuración para depuración
    logger.info(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # Configuración de cookies
    app.config.update(
        SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )

    # CORS configuration - Permitir solicitudes desde el frontend
    logger.info("Configurando CORS")
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Inicializar extensiones con la aplicación
    logger.info("Initializing extensions")
    db.init_app(app)
    logger.info("SQLAlchemy initialized")

    bcrypt.init_app(app)
    logger.info("Bcrypt initialized")

    jwt.init_app(app)
    logger.info("JWT initialized")

    migrate.init_app(app, db)
    logger.info("Migrate initialized")

    mail.init_app(app)
    logger.info("Mail initialized")

    # Crear todas las tablas si no existen
    with app.app_context():
        try:
            logger.info("Creating database tables if they don't exist")
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")


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
        """Create a standardized JSON error response"""
        return jsonify({
            "success": False,
            "message": message,
            "data": None
        }), status_code

    # Register error handlers
    # Note: IDE may show these functions as unused, but Flask uses them through decorators
    @app.errorhandler(404)
    def handle_not_found_error(error):
        """Handle 404 Not Found errors"""
        logger.warning(f"404 error: {error}")
        return make_error_response("Resource not found", 404)

    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"500 error: {error}")
        return make_error_response("Internal server error", 500)

    logger.info("Flask application created successfully")
    return app
