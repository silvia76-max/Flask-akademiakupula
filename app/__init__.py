from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv 
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail



bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
load_dotenv()
db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    
        
    # Configuración básica
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///akademiakupula.db'
<<<<<<< HEAD
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'tu-clave-secreta'  
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or 'otra-clave'  
=======
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'tu-clave-secreta'  # Usa la misma en todos lados
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or 'otra-clave' 
    app.config.update(
    SESSION_COOKIE_SECURE=False,  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
    # Configuración CORS (correctamente indentada dentro de create_app)
>>>>>>> e8c813ae5300349b59cca8d256b69a6df9b8e9e7
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
 
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)


    from app.routes.auth_routes import auth
    from app.routes.cursos import cursos_bp
    from app.routes.test_routes import test_bp
    from app.routes.contacto_routes import contacto_bp

    # Registrar blueprints
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(contacto_bp, url_prefix='/api/contacto')

    return app 
