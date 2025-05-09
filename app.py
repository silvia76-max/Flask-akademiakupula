"""
Archivo principal de la aplicación Flask.
Este archivo crea una instancia de la aplicación Flask y la ejecuta.
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración básica
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/akademiakupula.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or 'another-key'

# Inicializar extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Configurar CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Definir modelos
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Contacto(db.Model):
    __tablename__ = 'contactos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    curso = db.Column(db.String(50), nullable=True)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())

# Crear todas las tablas
with app.app_context():
    db.create_all()
    logger.info("Tablas creadas correctamente")

# Definir rutas
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API funcionando correctamente"})

@app.route('/api/auth/register', methods=['POST'])
def register():
    from flask import request
    from flask_jwt_extended import create_access_token
    
    try:
        logger.info("Recibida solicitud de registro")
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Validar datos
        if not all([data.get('full_name'), data.get('postal_code'), data.get('email'), data.get('password')]):
            return jsonify({"success": False, "message": "Todos los campos son obligatorios"}), 400
        
        # Verificar si el email ya está registrado
        existing_user = User.query.filter_by(email=data.get('email')).first()
        if existing_user:
            return jsonify({"success": False, "message": "Email ya registrado"}), 400
        
        # Crear nuevo usuario
        user = User(
            full_name=data.get('full_name'),
            postal_code=data.get('postal_code'),
            email=data.get('email'),
            is_confirmed=True
        )
        user.set_password(data.get('password'))
        
        # Guardar en la base de datos
        db.session.add(user)
        db.session.commit()
        logger.info(f"Usuario creado con ID: {user.id}")
        
        # Generar token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "success": True,
            "message": "Registro exitoso",
            "data": {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "postal_code": user.postal_code
                }
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en el registro: {str(e)}")
        return jsonify({"success": False, "message": f"Error en el registro: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    from flask import request
    from flask_jwt_extended import create_access_token
    
    try:
        logger.info("Recibida solicitud de login")
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Validar datos
        if not all([data.get('email'), data.get('password')]):
            return jsonify({"success": False, "message": "Email y contraseña son requeridos"}), 400
        
        # Buscar usuario
        user = User.query.filter_by(email=data.get('email')).first()
        if not user or not user.check_password(data.get('password')):
            return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
        
        # Generar token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso",
            "data": {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "postal_code": user.postal_code
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error en el login: {str(e)}")
        return jsonify({"success": False, "message": f"Error en el inicio de sesión: {str(e)}"}), 500

@app.route('/api/auth/profile', methods=['GET'])
def profile():
    from flask import request
    from flask_jwt_extended import get_jwt_identity
    
    try:
        # Obtener token de la cabecera
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Token no proporcionado"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verificar token
        from flask_jwt_extended import decode_token
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
        except Exception as e:
            return jsonify({"success": False, "message": f"Token inválido: {str(e)}"}), 401
        
        # Buscar usuario
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "message": "Perfil obtenido correctamente",
            "data": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "postal_code": user.postal_code
            }
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener perfil: {str(e)}")
        return jsonify({"success": False, "message": f"Error al obtener perfil: {str(e)}"}), 500

@app.route('/api/contacto', methods=['POST'])
def contacto():
    from flask import request
    
    try:
        logger.info("Recibida solicitud de contacto")
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Validar datos
        if not all([data.get('nombre'), data.get('email'), data.get('mensaje')]):
            return jsonify({"success": False, "message": "Nombre, email y mensaje son obligatorios"}), 400
        
        # Crear nuevo contacto
        contacto = Contacto(
            nombre=data.get('nombre'),
            email=data.get('email'),
            telefono=data.get('telefono', ''),
            curso=data.get('curso', ''),
            mensaje=data.get('mensaje')
        )
        
        # Guardar en la base de datos
        db.session.add(contacto)
        db.session.commit()
        logger.info(f"Contacto creado con ID: {contacto.id}")
        
        return jsonify({
            "success": True,
            "message": "Mensaje enviado correctamente",
            "data": {
                "id": contacto.id,
                "nombre": contacto.nombre,
                "email": contacto.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al enviar contacto: {str(e)}")
        return jsonify({"success": False, "message": f"Error al enviar contacto: {str(e)}"}), 500

# Ejecutar la aplicación
if __name__ == '__main__':
    logger.info("Iniciando servidor Flask")
    app.run(debug=True, host='0.0.0.0', port=5000)
