from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.contacto import Contacto
from app.models.session import Session  # Asegúrate de importar el modelo Session
from app.models.order import Order, OrderItem # Asegúrate de tener este modelo
from app import db
from app.utils.auth_middleware import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    """Endpoint para obtener datos del dashboard de administración"""
    try:
        # Obtener estadísticas básicas
        total_users = User.query.count()
        total_contacts = Contacto.query.count()
        
        # Obtener usuarios recientes
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_users_data = [user.to_dict() for user in recent_users]
        
        # Obtener contactos recientes
        recent_contacts = Contacto.query.order_by(Contacto.fecha_creacion.desc()).limit(5).all()
        recent_contacts_data = [contact.to_dict() for contact in recent_contacts]
        
        # Preparar datos para el dashboard
        dashboard_data = {
            "stats": {
                "total_users": total_users,
                "total_contacts": total_contacts,
                # Aquí puedes añadir más estadísticas según sea necesario
            },
            "recent_users": recent_users_data,
            "recent_contacts": recent_contacts_data
        }
        
        return jsonify({
            "success": True,
            "message": "Datos del dashboard obtenidos correctamente",
            "data": dashboard_data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener datos del dashboard: {str(e)}",
            "data": None
        }), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Endpoint para obtener todos los usuarios"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Obtener usuarios paginados
        users_pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Preparar datos de usuarios
        users_data = [user.to_dict() for user in users_pagination.items]
        
        return jsonify({
            "success": True,
            "message": "Usuarios obtenidos correctamente",
            "data": {
                "users": users_data,
                "pagination": {
                    "total": users_pagination.total,
                    "pages": users_pagination.pages,
                    "page": page,
                    "per_page": per_page,
                    "has_next": users_pagination.has_next,
                    "has_prev": users_pagination.has_prev
                }
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener usuarios: {str(e)}",
            "data": None
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """Endpoint para obtener un usuario específico"""
    try:
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            "success": True,
            "message": "Usuario obtenido correctamente",
            "data": user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener usuario: {str(e)}",
            "data": None
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Endpoint para actualizar un usuario"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Actualizar campos del usuario
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            user.email = data['email']
        if 'postal_code' in data:
            user.postal_code = data['postal_code']
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'is_confirmed' in data:
            user.is_confirmed = data['is_confirmed']
        if 'role_id' in data:
            user.role_id = data['role_id']
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Usuario actualizado correctamente",
            "data": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al actualizar usuario: {str(e)}",
            "data": None
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Endpoint para eliminar un usuario"""
    try:
        user = User.query.get_or_404(user_id)
        
        # No permitir eliminar al propio administrador
        current_user_id = get_jwt_identity()
        if user_id == current_user_id:
            return jsonify({
                "success": False,
                "message": "No puedes eliminar tu propio usuario",
                "data": None
            }), 400
        
        # Eliminar usuario
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Usuario eliminado correctamente",
            "data": None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al eliminar usuario: {str(e)}",
            "data": None
        }), 500

@admin_bp.route('/contacts', methods=['GET'])
@jwt_required()
@admin_required
def get_contacts():
    """Endpoint para obtener todos los mensajes de contacto"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Obtener contactos paginados
        contacts_pagination = Contacto.query.order_by(Contacto.fecha_creacion.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        # Preparar datos de contactos
        contacts_data = [contact.to_dict() for contact in contacts_pagination.items]
        
        return jsonify({
            "success": True,
            "message": "Mensajes de contacto obtenidos correctamente",
            "data": {
                "contacts": contacts_data,
                "pagination": {
                    "total": contacts_pagination.total,
                    "pages": contacts_pagination.pages,
                    "page": page,
                    "per_page": per_page,
                    "has_next": contacts_pagination.has_next,
                    "has_prev": contacts_pagination.has_prev
                }
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener mensajes de contacto: {str(e)}",
            "data": None
        }), 500

@admin_bp.route('/sessions', methods=['GET'])
@jwt_required()
@admin_required
def get_all_sessions():
    """Endpoint para obtener todas las sesiones de todos los usuarios (solo admin)"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        sessions_query = Session.query.order_by(Session.started_at.desc())
        pagination = sessions_query.paginate(page=page, per_page=per_page, error_out=False)
        sessions = [session.to_dict() for session in pagination.items]

        return jsonify({
            "success": True,
            "message": "Sesiones obtenidas correctamente",
            "data": {
                "sessions": sessions,
                "total": pagination.total,
                "page": pagination.page,
                "pages": pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener sesiones: {str(e)}",
            "data": None
        }), 500

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders():
    """Endpoint para obtener todos los pedidos (orders) de todos los usuarios (solo admin)"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        orders_query = Order.query.order_by(Order.created_at.desc())
        pagination = orders_query.paginate(page=page, per_page=per_page, error_out=False)
        orders = []
        for order in pagination.items:
            # Obtener los ítems del pedido desde la tabla orders_items
            items = OrderItem.query.filter_by(order_id=order.id).all()
            items_data = [item.to_dict() for item in items]
            order_data = order.to_dict()
            order_data['items'] = items_data
            orders.append(order_data)

        return jsonify({
            "success": True,
            "message": "Pedidos obtenidos correctamente",
            "data": {
                "orders": orders,
                "total": pagination.total,
                "page": pagination.page,
                "pages": pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener pedidos: {str(e)}",
            "data": None
        }), 500
