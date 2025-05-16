"""
Rutas para la gestión de sesiones de usuario.
"""

from flask import Blueprint, request, jsonify, g
from app import db
from app.models.session import Session
from app.auth.utils import token_required, get_user_from_token
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear un blueprint para las rutas de sesiones
sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/', methods=['GET'])
@token_required
def get_user_sessions():
    """Obtener todas las sesiones del usuario actual"""
    try:
        user_id = g.user.id
        logger.info(f"Obteniendo sesiones para el usuario {user_id}")

        sessions = Session.query.filter_by(user_id=user_id).order_by(Session.started_at.desc()).all()

        logger.info(f"Se encontraron {len(sessions)} sesiones para el usuario {user_id}")

        return jsonify({
            'success': True,
            'message': 'Sesiones obtenidas correctamente',
            'data': {
                'sessions': [session.to_dict() for session in sessions]
            }
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener sesiones: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Error al obtener sesiones: {str(e)}"
        }), 500

@sessions_bp.route('/current', methods=['GET'])
@token_required
def get_current_session():
    """Obtener la sesión actual del usuario"""
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        logger.info(f"Obteniendo sesión actual para el token: {token[:10]}...")

        session = Session.query.filter_by(token=token, is_active=True).first()

        if not session:
            logger.warning(f"Sesión no encontrada para el token: {token[:10]}...")
            return jsonify({
                'success': False,
                'message': 'Sesión no encontrada'
            }), 404

        # Actualizar la última actividad
        session.update_activity()
        db.session.commit()

        logger.info(f"Sesión actual obtenida correctamente: {session.id}")

        return jsonify({
            'success': True,
            'message': 'Sesión actual obtenida correctamente',
            'data': {
                'session': session.to_dict()
            }
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener sesión actual: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Error al obtener sesión actual: {str(e)}"
        }), 500

@sessions_bp.route('/<int:session_id>', methods=['DELETE'])
@token_required
def end_session(session_id):
    """Finalizar una sesión específica"""
    try:
        user_id = g.user.id
        logger.info(f"Finalizando sesión {session_id} para el usuario {user_id}")

        session = Session.query.filter_by(id=session_id, user_id=user_id).first()

        if not session:
            logger.warning(f"Sesión {session_id} no encontrada para el usuario {user_id}")
            return jsonify({
                'success': False,
                'message': 'Sesión no encontrada'
            }), 404

        session.end_session()
        db.session.commit()

        logger.info(f"Sesión {session_id} finalizada correctamente")

        return jsonify({
            'success': True,
            'message': 'Sesión finalizada correctamente'
        }), 200
    except Exception as e:
        logger.error(f"Error al finalizar sesión {session_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Error al finalizar sesión: {str(e)}"
        }), 500

@sessions_bp.route('/all', methods=['DELETE'])
@token_required
def end_all_sessions():
    """Finalizar todas las sesiones del usuario excepto la actual"""
    try:
        user_id = g.user.id
        token = request.headers.get('Authorization').split(' ')[1]

        logger.info(f"Finalizando todas las sesiones para el usuario {user_id} excepto la actual")

        # Obtener todas las sesiones activas excepto la actual
        sessions = Session.query.filter(
            Session.user_id == user_id,
            Session.token != token,
            Session.is_active == True
        ).all()

        logger.info(f"Se encontraron {len(sessions)} sesiones activas para finalizar")

        for session in sessions:
            session.end_session()

        db.session.commit()

        logger.info(f"Se finalizaron {len(sessions)} sesiones correctamente")

        return jsonify({
            'success': True,
            'message': 'Todas las otras sesiones han sido finalizadas',
            'data': {
                'count': len(sessions)
            }
        }), 200
    except Exception as e:
        logger.error(f"Error al finalizar todas las sesiones: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Error al finalizar todas las sesiones: {str(e)}"
        }), 500