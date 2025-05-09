"""
Servidor Flask simple para manejar registro y login.
Este archivo es independiente y no depende de la estructura existente.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import hashlib
import secrets
import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar CORS para permitir solicitudes desde el frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
})

# Ruta a la base de datos
DB_PATH = os.path.join('instance', 'simple_db.sqlite')

# Asegurarse de que el directorio instance existe
if not os.path.exists('instance'):
    os.makedirs('instance')
    logger.info("Directorio 'instance' creado")

# Función para inicializar la base de datos
def init_db():
    """Inicializa la base de datos con las tablas necesarias."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        postal_code TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_confirmed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Crear tabla de contactos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contactos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL,
        telefono TEXT,
        curso TEXT,
        mensaje TEXT NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Crear tabla de tokens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Base de datos inicializada correctamente")

# Inicializar la base de datos
init_db()

# Funciones de utilidad
def hash_password(password):
    """Genera un hash seguro para la contraseña."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = hashlib.sha256(pwdhash).hexdigest()
    return (salt + pwdhash.encode('ascii')).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
    salt = stored_password[:64]
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = hashlib.sha256(pwdhash).hexdigest()
    return pwdhash == stored_hash

def generate_token():
    """Genera un token aleatorio."""
    return secrets.token_hex(32)

# Rutas de la API
@app.route('/api/test', methods=['GET'])
def test():
    """Endpoint de prueba para verificar que el servidor está funcionando."""
    return jsonify({"message": "API funcionando correctamente"})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Endpoint para registrar un nuevo usuario."""
    try:
        logger.info("Recibida solicitud de registro")
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Validar datos
        required_fields = ['full_name', 'postal_code', 'email', 'password']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": "Todos los campos son obligatorios"}), 400
        
        full_name = data.get('full_name')
        postal_code = data.get('postal_code')
        email = data.get('email')
        password = data.get('password')
        
        # Validar longitud de contraseña
        if len(password) < 6:
            return jsonify({"success": False, "message": "La contraseña debe tener al menos 6 caracteres"}), 400
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si el email ya está registrado
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Email ya registrado"}), 400
        
        # Generar hash de la contraseña
        password_hash = hash_password(password)
        
        # Insertar nuevo usuario
        cursor.execute(
            "INSERT INTO users (full_name, postal_code, email, password_hash, is_confirmed) VALUES (?, ?, ?, ?, ?)",
            (full_name, postal_code, email, password_hash, 1)  # is_confirmed = 1 para confirmar automáticamente
        )
        conn.commit()
        
        # Obtener el ID del usuario insertado
        user_id = cursor.lastrowid
        
        # Generar token
        token = generate_token()
        
        # Guardar token
        cursor.execute(
            "INSERT INTO tokens (user_id, token) VALUES (?, ?)",
            (user_id, token)
        )
        conn.commit()
        
        # Obtener datos del usuario
        cursor.execute("SELECT id, full_name, email, postal_code FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        logger.info(f"Usuario registrado con ID: {user_id}")
        
        return jsonify({
            "success": True,
            "message": "Registro exitoso",
            "data": {
                "access_token": token,
                "user": {
                    "id": user[0],
                    "full_name": user[1],
                    "email": user[2],
                    "postal_code": user[3]
                }
            }
        }), 201
    except Exception as e:
        logger.error(f"Error en el registro: {str(e)}")
        return jsonify({"success": False, "message": f"Error en el registro: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint para iniciar sesión."""
    try:
        logger.info("Recibida solicitud de login")
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Validar datos
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Email y contraseña son requeridos"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar usuario
        cursor.execute("SELECT id, full_name, email, postal_code, password_hash, is_confirmed FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
        
        # Verificar contraseña
        if not verify_password(user[4], password):
            conn.close()
            return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
        
        # Verificar si la cuenta está confirmada
        if not user[5]:
            # Confirmar automáticamente
            cursor.execute("UPDATE users SET is_confirmed = 1 WHERE id = ?", (user[0],))
            conn.commit()
        
        # Generar token
        token = generate_token()
        
        # Guardar token
        cursor.execute(
            "INSERT INTO tokens (user_id, token) VALUES (?, ?)",
            (user[0], token)
        )
        conn.commit()
        
        conn.close()
        
        logger.info(f"Usuario {email} ha iniciado sesión")
        
        return jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso",
            "data": {
                "access_token": token,
                "user": {
                    "id": user[0],
                    "full_name": user[1],
                    "email": user[2],
                    "postal_code": user[3]
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error en el login: {str(e)}")
        return jsonify({"success": False, "message": f"Error en el inicio de sesión: {str(e)}"}), 500

@app.route('/api/auth/profile', methods=['GET'])
def profile():
    """Endpoint para obtener el perfil del usuario."""
    try:
        logger.info("Recibida solicitud de perfil")
        
        # Obtener token de la cabecera
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Token no proporcionado"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar token
        cursor.execute("""
            SELECT u.id, u.full_name, u.email, u.postal_code 
            FROM users u
            JOIN tokens t ON u.id = t.user_id
            WHERE t.token = ?
        """, (token,))
        
        user = cursor.fetchone()
        
        conn.close()
        
        if not user:
            return jsonify({"success": False, "message": "Token inválido o expirado"}), 401
        
        logger.info(f"Perfil obtenido para usuario ID: {user[0]}")
        
        return jsonify({
            "success": True,
            "message": "Perfil obtenido correctamente",
            "data": {
                "id": user[0],
                "full_name": user[1],
                "email": user[2],
                "postal_code": user[3]
            }
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener perfil: {str(e)}")
        return jsonify({"success": False, "message": f"Error al obtener perfil: {str(e)}"}), 500

@app.route('/api/contacto', methods=['POST'])
def contacto():
    """Endpoint para enviar un mensaje de contacto."""
    try:
        logger.info("Recibida solicitud de contacto")
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Validar datos
        required_fields = ['nombre', 'email', 'mensaje']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": "Nombre, email y mensaje son obligatorios"}), 400
        
        nombre = data.get('nombre')
        email = data.get('email')
        telefono = data.get('telefono', '')
        curso = data.get('curso', '')
        mensaje = data.get('mensaje')
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insertar contacto
        cursor.execute(
            "INSERT INTO contactos (nombre, email, telefono, curso, mensaje) VALUES (?, ?, ?, ?, ?)",
            (nombre, email, telefono, curso, mensaje)
        )
        conn.commit()
        
        # Obtener el ID del contacto insertado
        contacto_id = cursor.lastrowid
        
        conn.close()
        
        logger.info(f"Contacto registrado con ID: {contacto_id}")
        
        return jsonify({
            "success": True,
            "message": "Mensaje enviado correctamente",
            "data": {
                "id": contacto_id,
                "nombre": nombre,
                "email": email
            }
        }), 201
    except Exception as e:
        logger.error(f"Error al enviar contacto: {str(e)}")
        return jsonify({"success": False, "message": f"Error al enviar contacto: {str(e)}"}), 500

# Ejecutar la aplicación
if __name__ == '__main__':
    logger.info("Iniciando servidor Flask simple")
    app.run(debug=True, host='0.0.0.0', port=5000)
