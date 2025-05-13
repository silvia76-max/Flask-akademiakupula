from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User

def admin_required(fn):
    """
    Decorador para proteger rutas que requieren permisos de administrador.
    Debe usarse después del decorador jwt_required().
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verificar que hay un token JWT válido
        verify_jwt_in_request()
        
        # Obtener el ID del usuario del token
        current_user_id = get_jwt_identity()
        
        # Obtener el usuario de la base de datos
        user = User.query.get(current_user_id)
        
        # Verificar si el usuario es administrador
        if not user or not user.is_admin:
            return jsonify({
                "success": False,
                "message": "Se requieren permisos de administrador para acceder a este recurso",
                "data": None
            }), 403
        
        # Si el usuario es administrador, continuar con la función original
        return fn(*args, **kwargs)
    
    return wrapper

def role_required(role_name):
    """
    Decorador para proteger rutas que requieren un rol específico.
    Debe usarse después del decorador jwt_required().
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificar que hay un token JWT válido
            verify_jwt_in_request()
            
            # Obtener el ID del usuario del token
            current_user_id = get_jwt_identity()
            
            # Obtener el usuario de la base de datos
            user = User.query.get(current_user_id)
            
            # Verificar si el usuario tiene el rol requerido
            if not user or not user.has_role(role_name):
                return jsonify({
                    "success": False,
                    "message": f"Se requiere el rol '{role_name}' para acceder a este recurso",
                    "data": None
                }), 403
            
            # Si el usuario tiene el rol requerido, continuar con la función original
            return fn(*args, **kwargs)
        
        return wrapper
    
    return decorator
