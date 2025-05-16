"""
Utilidades para la autenticación.
"""

import os
import jwt
from functools import wraps
from flask import request, jsonify, g
from app.models.user import User
from app.models.session import Session
from datetime import datetime, timezone
import logging

# Configurar logger
logger = logging.getLogger(__name__)

def token_required(f):
    """
    Decorador para verificar el token JWT en las solicitudes.
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar si hay un token en el encabezado Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token no proporcionado'
            }), 401
        
        try:
            # Decodificar el token
            payload = jwt.decode(
                token, 
                os.environ.get('SECRET_KEY', 'tu_clave_secreta_predeterminada'),
                algorithms=['HS256']
            )
            
            # Obtener el usuario
            user = User.query.get(payload['sub'])
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }), 401
            
            # Verificar si la sesión está activa
            session = Session.query.filter_by(token=token, is_active=True).first()
            
            if not session:
                return jsonify({
                    'success': False,
                    'message': 'Sesión inválida o expirada'
                }), 401
            
            # Actualizar la última actividad de la sesión
            session.update_activity()
            
            # Guardar el usuario en el contexto global
            g.user = user
            g.token = token
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expirado'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Token inválido'
            }), 401
        
    return decorated

def get_user_from_token(token):
    """
    Obtiene el usuario a partir de un token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        Usuario o None si el token es inválido
    """
    try:
        # Decodificar el token
        payload = jwt.decode(
            token, 
            os.environ.get('SECRET_KEY', 'tu_clave_secreta_predeterminada'),
            algorithms=['HS256']
        )
        
        # Obtener el usuario
        user = User.query.get(payload['sub'])
        
        return user
    except:
        return None
