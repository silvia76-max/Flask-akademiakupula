"""
Rutas de autenticación para la API.
Este módulo contiene las rutas para registro, login, perfil y otras funcionalidades relacionadas con la autenticación.
"""

from flask import Blueprint, request, current_app, jsonify, g
from app.models.user import User
from app import db, mail, cache, limiter
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import logging
from datetime import datetime, timezone
from app.utils import validate_email, validate_required_fields, standardize_response, log_api_call
from app.models.session import Session
import os
import jwt

# Configurar logger
logger = logging.getLogger(__name__)

# Crear blueprint
auth = Blueprint('auth', __name__)

# El serializador se inicializará en cada función que lo necesite
# para evitar acceder a current_app fuera del contexto de la aplicación

@auth.route('/register', methods=['POST'])
@limiter.limit("10/hour")  # Limitar a 10 registros por hora por IP
@log_api_call
def register():
    """Registra un nuevo usuario."""
    try:
        # Registrar en un archivo para depuración
        with open('register_debug.log', 'a') as f:
            f.write("Recibida solicitud de registro\n")

        logger.info("Recibida solicitud de registro")
        data = request.get_json()

        # Registrar datos recibidos
        with open('register_debug.log', 'a') as f:
            f.write(f"Datos recibidos: {data}\n")

        # Validar campos requeridos
        required_fields = ['full_name', 'postal_code', 'email', 'password']
        valid, missing_fields = validate_required_fields(data, required_fields)

        if not valid:
            logger.warning(f"Faltan campos obligatorios: {missing_fields}")
            with open('register_debug.log', 'a') as f:
                f.write(f"Faltan campos obligatorios: {missing_fields}\n")
            return standardize_response(
                False,
                f"Faltan campos obligatorios: {', '.join(missing_fields)}",
                status_code=400
            )

        full_name = data.get('full_name')
        postal_code = data.get('postal_code')
        email = data.get('email')
        password = data.get('password')

        # Validar formato de email
        if not validate_email(email):
            logger.warning(f"Formato de email inválido: {email}")
            with open('register_debug.log', 'a') as f:
                f.write(f"Formato de email inválido: {email}\n")
            return standardize_response(False, "Formato de email inválido", status_code=400)

        # Validar longitud de contraseña
        if len(password) < 8:
            logger.warning("Contraseña demasiado corta")
            with open('register_debug.log', 'a') as f:
                f.write("Contraseña demasiado corta\n")
            return standardize_response(
                False,
                "La contraseña debe tener al menos 8 caracteres",
                status_code=400
            )

        # Verificar si el email ya está registrado
        with open('register_debug.log', 'a') as f:
            f.write(f"Verificando si el email ya está registrado: {email}\n")

        existing_user = User.get_by_email(email)
        if existing_user:
            logger.warning(f"Email ya registrado: {email}")
            with open('register_debug.log', 'a') as f:
                f.write(f"Email ya registrado: {email}\n")
            return standardize_response(False, "Email ya registrado", status_code=400)

        # Crear nuevo usuario usando el método de clase
        with open('register_debug.log', 'a') as f:
            f.write(f"Creando nuevo usuario: {full_name}, {email}\n")

        try:
            # Crear usuario directamente sin usar el método de clase
            with open('register_debug.log', 'a') as f:
                f.write("Creando usuario directamente en la ruta\n")

            # Crear instancia de usuario
            user = User(
                full_name=full_name,
                email=email,
                postal_code=postal_code,
                is_confirmed=True  # Confirmación automática para simplificar
            )

            with open('register_debug.log', 'a') as f:
                f.write("Usuario instanciado correctamente\n")

            # Establecer contraseña
            user.set_password(password)

            with open('register_debug.log', 'a') as f:
                f.write("Contraseña establecida correctamente\n")

            # Añadir a la sesión y hacer commit
            db.session.add(user)

            with open('register_debug.log', 'a') as f:
                f.write("Usuario añadido a la sesión\n")

            db.session.commit()

            with open('register_debug.log', 'a') as f:
                f.write(f"Usuario creado con ID: {user.id}\n")

            logger.info(f"Usuario creado con ID: {user.id}")

            # Generar tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            # Invalidar caché
            cache.delete_memoized(User.get_by_email, User, email)

            return standardize_response(
                True,
                "Registro exitoso. Tu cuenta ha sido activada automáticamente.",
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user.to_dict()
                },
                status_code=201
            )
        except Exception as e:
            with open('register_debug.log', 'a') as f:
                f.write(f"Error al crear usuario: {str(e)}\n")
            raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en el registro: {str(e)}", exc_info=True)
        with open('register_debug.log', 'a') as f:
            f.write(f"Error en el registro: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        return standardize_response(False, "Error en el registro", status_code=500)

@auth.route('/confirm-email/<token>', methods=['GET'])
@limiter.limit("10/hour")  # Limitar a 10 confirmaciones por hora por IP
@log_api_call
def confirm_email(token):
    """Confirma la cuenta de un usuario a través de un token enviado por email."""
    try:
        # Inicializar serializador dentro del contexto de la aplicación
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

        # Desencriptar el token
        email = s.loads(token, salt='email-confirm', max_age=3600)
        logger.info(f"Solicitud de confirmación para email: {email}")

        # Buscar usuario por email
        user = User.get_by_email(email)

        if not user:
            logger.warning(f"Usuario no encontrado para confirmación: {email}")
            return standardize_response(False, "Usuario no encontrado", status_code=404)

        # Verificar si ya está confirmado
        if user.is_confirmed:
            logger.info(f"Cuenta ya confirmada: {email}")
            return standardize_response(
                True,
                "Cuenta ya confirmada",
                {"email": email}
            )

        # Confirmar cuenta
        user.is_confirmed = True
        db.session.commit()
        logger.info(f"Cuenta confirmada correctamente: {email}")

        # Invalidar caché
        cache.delete_memoized(User.get_by_email, User, email)

        return standardize_response(
            True,
            "Cuenta confirmada correctamente",
            {"email": email}
        )
    except SignatureExpired:
        logger.warning(f"Token de confirmación expirado: {token[:10]}...")
        return standardize_response(
            False,
            "El enlace de confirmación ha expirado",
            status_code=400
        )
    except BadSignature:
        logger.warning(f"Token de confirmación inválido: {token[:10]}...")
        return standardize_response(
            False,
            "El enlace de confirmación es inválido",
            status_code=400
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al confirmar email: {str(e)}", exc_info=True)
        return standardize_response(
            False,
            "Error al confirmar email",
            status_code=500
        )

@auth.route('/login', methods=['POST'])
@limiter.limit("20/minute")  # Limitar a 20 intentos de login por minuto por IP
@log_api_call
def login():
    """Inicia sesión de un usuario."""
    try:
        logger.info("Recibida solicitud de login")
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['email', 'password']
        valid, missing_fields = validate_required_fields(data, required_fields)

        if not valid:
            logger.warning(f"Faltan campos obligatorios: {missing_fields}")
            return standardize_response(
                False,
                f"Faltan campos obligatorios: {', '.join(missing_fields)}",
                status_code=400
            )

        email = data.get('email')
        password = data.get('password')

        # Buscar usuario por email
        user = User.get_by_email(email)

        if not user:
            logger.warning(f"Usuario no encontrado: {email}")
            return standardize_response(False, "Credenciales inválidas", status_code=401)

        # Verificar si la cuenta está bloqueada
        if user.is_locked:
            logger.warning(f"Cuenta bloqueada: {email}")
            return standardize_response(
                False,
                "Cuenta bloqueada temporalmente por múltiples intentos fallidos",
                status_code=401
            )

        # Verificar contraseña
        if not user.check_password(password):
            # El método check_password ya incrementa los intentos fallidos
            db.session.commit()
            logger.warning(f"Contraseña incorrecta para: {email}")
            return standardize_response(False, "Credenciales inválidas", status_code=401)

        # Verificar si la cuenta está confirmada
        if not user.is_confirmed:
            logger.warning(f"Cuenta no confirmada: {email}")
            # Confirmar automáticamente para simplificar
            user.is_confirmed = True

        # Actualizar último login
        user.last_login = datetime.now(timezone.utc)

        # Generar tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Registrar la sesión
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')

        try:
            # Crear nueva sesión
            new_session = Session(
                user_id=user.id,
                token=access_token,
                ip_address=ip_address,
                user_agent=user_agent
            )

            db.session.add(new_session)
            db.session.commit()

            logger.info(f"Sesión creada para usuario {user.id}: {new_session.id}")
        except Exception as e:
            logger.error(f"Error al crear sesión: {str(e)}", exc_info=True)
            # Continuamos aunque falle la creación de la sesión
            db.session.rollback()
            db.session.commit()  # Commit para guardar al menos el último login

        logger.info(f"Login exitoso: {email}")

        return standardize_response(
            True,
            "Inicio de sesión exitoso",
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }
        )
    except Exception as e:
        logger.error(f"Error en el login: {str(e)}", exc_info=True)
        return standardize_response(False, "Error en el inicio de sesión", status_code=500)





@auth.route('/logout', methods=['POST'])
@jwt_required()
@log_api_call
def logout():
    """Cierra la sesión actual del usuario"""
    try:
        # Obtener el token del encabezado Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return standardize_response(False, "Token no proporcionado", status_code=401)

        token = auth_header.split(' ')[1]

        # Buscar la sesión activa con este token
        session = Session.query.filter_by(token=token, is_active=True).first()

        if session:
            # Finalizar la sesión
            session.end_session()
            db.session.commit()
            logger.info(f"Sesión {session.id} cerrada correctamente")
        else:
            logger.warning(f"No se encontró una sesión activa para el token proporcionado")

        return standardize_response(True, "Sesión cerrada correctamente")
    except Exception as e:
        logger.error(f"Error al cerrar sesión: {str(e)}", exc_info=True)
        return standardize_response(False, f"Error al cerrar sesión: {str(e)}", status_code=500)

@auth.route('/profile', methods=['GET'])
@jwt_required()
@log_api_call
def profile():
    """Obtiene el perfil del usuario autenticado."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            logger.warning(f"Usuario no encontrado: {user_id}")
            return standardize_response(False, "Usuario no encontrado", status_code=404)

        logger.info(f"Perfil obtenido: {user.email}")

        return standardize_response(
            True,
            "Perfil obtenido correctamente",
            user.to_dict()
        )
    except Exception as e:
        logger.error(f"Error al obtener perfil: {str(e)}", exc_info=True)
        return standardize_response(False, "Error al obtener perfil", status_code=500)

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@log_api_call
def refresh():
    """Refresca el token de acceso usando un token de refresco."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_active:
            logger.warning(f"Usuario inactivo o no encontrado: {user_id}")
            return standardize_response(False, "Usuario no encontrado o inactivo", status_code=401)

        # Generar nuevo token de acceso
        access_token = create_access_token(identity=user_id)

        logger.info(f"Token refrescado para usuario: {user.email}")

        return standardize_response(
            True,
            "Token refrescado correctamente",
            {"access_token": access_token}
        )
    except Exception as e:
        logger.error(f"Error al refrescar token: {str(e)}", exc_info=True)
        return standardize_response(False, "Error al refrescar token", status_code=500)

