"""
Utilidades para la aplicación.
"""

from flask import jsonify
import functools
import logging
import re

# Configurar logger
logger = logging.getLogger(__name__)

# Importar funciones de correo electrónico
from app.utils.email_utils import (
    send_verification_email,
    send_password_reset_email,
    send_welcome_email
)

def standardize_response(success, message, data=None, status_code=200):
    """
    Estandariza las respuestas de la API.

    Args:
        success (bool): Indica si la operación fue exitosa
        message (str): Mensaje descriptivo
        data (dict, optional): Datos a devolver. Defaults to None.
        status_code (int, optional): Código de estado HTTP. Defaults to 200.

    Returns:
        tuple: Respuesta JSON y código de estado
    """
    response = {
        "success": success,
        "message": message
    }

    if data is not None:
        response["data"] = data

    return jsonify(response), status_code

def log_api_call(f):
    """
    Decorador para registrar llamadas a la API.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"API call: {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function

def validate_email(email):
    """
    Valida que un email tenga un formato correcto.

    Args:
        email (str): Email a validar

    Returns:
        bool: True si el email es válido, False en caso contrario
    """
    # Patrón básico para validar emails
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_required_fields(data, required_fields):
    """
    Valida que todos los campos requeridos estén presentes en los datos.

    Args:
        data (dict): Datos a validar
        required_fields (list): Lista de campos requeridos

    Returns:
        tuple: (bool, list) - (True si todos los campos están presentes, lista de campos faltantes)
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)

    return len(missing_fields) == 0, missing_fields
