from flask import Blueprint, request, jsonify, url_for
from app.models import User
from app import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import Config
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__)
s = URLSafeTimedSerializer(Config.SECRET_KEY)

@auth.route('/register', methods=['POST'])
def register():
    try:
        print("Recibida solicitud de registro")
        data = request.get_json()
        print(f"Datos recibidos: {data}")

        full_name = data.get('full_name')
        postal_code = data.get('postal_code')
        email = data.get('email')
        password = data.get('password')

        # Validar que todos los campos requeridos estén presentes
        if not all([full_name, postal_code, email, password]):
            print("Error: Faltan campos obligatorios")
            return jsonify({"success": False, "message": "Todos los campos son obligatorios"}), 400

        # Validar formato de email
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Error: Formato de email inválido")
            return jsonify({"success": False, "message": "Formato de email inválido"}), 400

        # Validar longitud de contraseña
        if len(password) < 6:
            print("Error: Contraseña demasiado corta")
            return jsonify({"success": False, "message": "La contraseña debe tener al menos 6 caracteres"}), 400

        # Verificar si el email ya está registrado
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"Error: Email {email} ya registrado")
            return jsonify({"success": False, "message": "Email ya registrado"}), 400

        # Crear nuevo usuario
        print(f"Creando nuevo usuario: {full_name}, {email}")
        user = User(full_name=full_name, postal_code=postal_code, email=email)
        user.set_password(password)

        # Marcar como confirmado automáticamente
        user.is_confirmed = True

        # Guardar en la base de datos
        db.session.add(user)
        db.session.commit()
        print(f"Usuario creado con ID: {user.id}")

        # Generar token para inicio de sesión automático
        access_token = create_access_token(identity=user.id)

        return jsonify({
            "success": True,
            "message": "Registro exitoso. Tu cuenta ha sido activada automáticamente.",
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
        print(f"Error en el registro: {str(e)}")
        return jsonify({"success": False, "message": f"Error en el registro: {str(e)}"}), 500

@auth.route('/confirm-email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)

        user = User.query.filter_by(email=email).first_or_404()

        if user.is_confirmed:
            return jsonify({
                "success": True,
                "message": "Cuenta ya confirmada.",
                "data": {"email": email}
            }), 200

        user.is_confirmed = True
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Cuenta confirmada correctamente.",
            "data": {"email": email}
        }), 200
    except SignatureExpired:
        return jsonify({
            "success": False,
            "message": "El enlace de confirmación ha expirado.",
            "data": None
        }), 400
    except BadSignature:
        return jsonify({
            "success": False,
            "message": "El enlace de confirmación es inválido.",
            "data": None
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al confirmar email: {str(e)}",
            "data": None
        }), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        print("Recibida solicitud de login")
        data = request.get_json()
        print(f"Datos recibidos: {data}")

        # Validar que se proporcionaron email y password
        if not data or 'email' not in data or 'password' not in data:
            print("Error: Faltan email o contraseña")
            return jsonify({
                "success": False,
                "message": "Email y contraseña son requeridos"
            }), 400

        email = data.get('email')
        password = data.get('password')

        # Buscar usuario por email
        print(f"Buscando usuario con email: {email}")
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"Error: Usuario con email {email} no encontrado")
            return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

        # Verificar contraseña
        if not user.check_password(password):
            print("Error: Contraseña incorrecta")
            return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

        # Verificar si la cuenta está confirmada
        if not user.is_confirmed:
            print(f"Error: Usuario {email} no confirmado")
            # Confirmar automáticamente para simplificar
            user.is_confirmed = True
            db.session.commit()
            print(f"Usuario {email} confirmado automáticamente")

        # Generar token con tiempo de expiración (1 día)
        print(f"Generando token para usuario ID: {user.id}")
        access_token = create_access_token(identity=user.id)
        print(f"Token generado: {access_token[:10]}...")

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
        print(f"Error en el login: {str(e)}")
        return jsonify({"success": False, "message": f"Error en el inicio de sesión: {str(e)}"}), 500

@auth.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        return jsonify({
            "success": True,
            "message": "Bienvenido a tu perfil",
            "data": {
                "full_name": user.full_name,
                "email": user.email,
                "postal_code": user.postal_code,
                "id": user.id
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al obtener perfil: {str(e)}"}), 500

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # En una implementación real, aquí podrías añadir el token a una lista negra
        # para invalidarlo antes de su expiración
        return jsonify({
            "success": True,
            "message": "Sesión cerrada correctamente",
            "data": None
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al cerrar sesión: {str(e)}"}), 500