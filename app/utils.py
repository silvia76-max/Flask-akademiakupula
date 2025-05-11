"""
Utilidades para la aplicación Flask.
Este módulo contiene funciones de utilidad que se utilizan en toda la aplicación.
"""

import re
import json
import time
import logging
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db, cache

logger = logging.getLogger(__name__)

def validate_email(email):
    """
    Valida que una cadena tenga formato de correo electrónico.
    
    Args:
        email (str): Correo electrónico a validar
        
    Returns:
        bool: True si el correo es válido, False en caso contrario
    """
    if not email:
        return False
    
    # Patrón básico para validar correos electrónicos
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_required_fields(data, required_fields):
    """
    Valida que todos los campos requeridos estén presentes en los datos.
    
    Args:
        data (dict): Datos a validar
        required_fields (list): Lista de campos requeridos
        
    Returns:
        tuple: (bool, list) - Éxito de la validación y lista de campos faltantes
    """
    if not data:
        return False, required_fields
    
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    return len(missing_fields) == 0, missing_fields

def standardize_response(success, message, data=None, status_code=200, errors=None):
    """
    Crea una respuesta JSON estandarizada.
    
    Args:
        success (bool): Indica si la operación fue exitosa
        message (str): Mensaje descriptivo
        data (any, optional): Datos a devolver. Por defecto None.
        status_code (int, optional): Código de estado HTTP. Por defecto 200.
        errors (list, optional): Lista de errores. Por defecto None.
        
    Returns:
        tuple: (dict, int) - Respuesta JSON y código de estado
    """
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), status_code

def timed_lru_cache(seconds=300, maxsize=128):
    """
    Decorador para cachear resultados de funciones con expiración por tiempo.
    
    Args:
        seconds (int, optional): Tiempo de expiración en segundos. Por defecto 300.
        maxsize (int, optional): Tamaño máximo de la caché. Por defecto 128.
        
    Returns:
        function: Decorador configurado
    """
    def decorator(func):
        # Usar el decorador de caché de Flask
        @cache.memoize(timeout=seconds)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(func):
    """
    Decorador para requerir que el usuario sea administrador.
    
    Args:
        func (function): Función a decorar
        
    Returns:
        function: Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Verificar token JWT
            verify_jwt_in_request()
            
            # Obtener ID de usuario
            user_id = get_jwt_identity()
            
            # Aquí deberías verificar si el usuario es administrador
            # Por ejemplo, consultando la base de datos
            # Esta es una implementación de ejemplo
            from app.models.user import User
            user = User.query.get(user_id)
            
            if not user or not getattr(user, 'is_admin', False):
                return standardize_response(
                    False, 
                    "Se requieren privilegios de administrador", 
                    status_code=403
                )
            
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en admin_required: {str(e)}")
            return standardize_response(
                False, 
                "Error de autenticación", 
                status_code=401
            )
    return wrapper

def log_api_call(func):
    """
    Decorador para registrar llamadas a la API.
    
    Args:
        func (function): Función a decorar
        
    Returns:
        function: Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Registrar información de la solicitud
        logger.info(f"API Call: {request.method} {request.path}")
        logger.debug(f"Headers: {dict(request.headers)}")
        
        if request.is_json:
            # Evitar registrar información sensible como contraseñas
            safe_data = request.get_json().copy() if request.get_json() else {}
            if 'password' in safe_data:
                safe_data['password'] = '********'
            logger.debug(f"Request data: {safe_data}")
        
        # Ejecutar la función original
        result = func(*args, **kwargs)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Registrar información de la respuesta
        if isinstance(result, tuple) and len(result) >= 2:
            response, status_code = result[0], result[1]
            logger.info(f"Response: {status_code} (processed in {process_time:.4f}s)")
        else:
            logger.info(f"Response: (processed in {process_time:.4f}s)")
        
        return result
    return wrapper
