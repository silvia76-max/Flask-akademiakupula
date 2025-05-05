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


# Inicializar extensiones (fuera de create_app para poder importarlas en otros archivos)
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
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'tu-clave-secreta'  # Usa la misma en todos lados
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or 'otra-clave'  # Solo para sesiones
    # Configuración CORS (correctamente indentada dentro de create_app)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Inicializar extensiones con la app (también indentado correctamente)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Importar blueprints aquí para evitar importaciones circulares
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
