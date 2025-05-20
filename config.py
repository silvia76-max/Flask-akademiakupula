import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """Configuración base para la aplicación Flask."""

    # Entorno
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    TESTING = os.getenv('FLASK_TESTING', 'False') == 'True'

    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///akademiakupula.db')
    # Asegurarse de que la URL no contenga caracteres de escape
    if isinstance(SQLALCHEMY_DATABASE_URI, str) and '\\x3a' in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('\\x3a', ':')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }

    # Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Cookies y sesiones
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Correo electrónico
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_MAX_EMAILS = 20
    MAIL_ASCII_ATTACHMENTS = False

    # URLs
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

    # CORS
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5174',
        'http://127.0.0.1:5174',
        'http://localhost',
        'http://127.0.0.1',
        os.getenv('FRONTEND_URL', '')
    ]

    # Rendimiento
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutos

    # Límites de tasa (rate limiting)
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True') == 'True'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200 per day, 50 per hour')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')

    # Compresión
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

    # Configuración de uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
