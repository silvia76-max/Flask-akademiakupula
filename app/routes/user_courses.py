"""
Rutas para la gestión de la lista de deseos y el carrito de compras.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, cache, limiter
from app.models.user import User
from app.models.curso import Curso
from app.models.wishlist import Wishlist
from app.models.cart import Cart
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.utils import standardize_response, log_api_call

# Configurar logger
logger = logging.getLogger(__name__)

# Crear blueprint
user_courses_bp = Blueprint('user_courses', __name__)

# Endpoint para obtener la lista de deseos del usuario
@user_courses_bp.route('/wishlist', methods=['GET'])
@jwt_required()
@log_api_call
def get_wishlist():
    """Obtiene la lista de deseos del usuario autenticado."""
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()

        # Buscar los cursos en la lista de deseos del usuario
        wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()

        # Obtener los detalles de cada curso
        wishlist = []
        for item in wishlist_items:
            curso = Curso.query.get(item.curso_id)
            if curso:
                curso_dict = curso.to_dict()
                wishlist.append({
                    'wishlist_id': item.id,
                    'curso': curso_dict
                })

        logger.info(f"Lista de deseos obtenida para usuario {user_id}: {len(wishlist)} cursos")

        return standardize_response(
            True,
            "Lista de deseos obtenida correctamente",
            {"wishlist": wishlist}
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al obtener la lista de deseos: {str(e)}", exc_info=True)
        return standardize_response(
            False,
            "Error al obtener la lista de deseos",
            status_code=500
        )

# Endpoint para añadir un curso a la lista de deseos
@user_courses_bp.route('/wishlist', methods=['POST'])
@jwt_required()
@limiter.limit("20/minute")
@log_api_call
def add_to_wishlist():
    """Añade un curso a la lista de deseos del usuario autenticado."""
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()

        # Obtener el ID del curso desde el cuerpo de la solicitud
        data = request.get_json()
        curso_id = data.get('curso_id')

        if not curso_id:
            logger.warning(f"Intento de añadir curso a wishlist sin ID de curso: usuario {user_id}")
            return standardize_response(
                False,
                "Se requiere el ID del curso",
                status_code=400
            )

        # Verificar si el curso existe
        curso = Curso.query.get(curso_id)
        if not curso:
            logger.warning(f"Intento de añadir curso inexistente a wishlist: usuario {user_id}, curso {curso_id}")
            return standardize_response(
                False,
                "El curso no existe",
                status_code=404
            )

        # Verificar si el curso ya está en la lista de deseos
        existing_item = Wishlist.query.filter_by(
            user_id=user_id,
            curso_id=curso_id
        ).first()

        if existing_item:
            logger.info(f"Curso ya en wishlist: usuario {user_id}, curso {curso_id}")
            return standardize_response(
                False,
                "El curso ya está en la lista de deseos",
                status_code=400
            )

        # Añadir el curso a la lista de deseos
        wishlist_item = Wishlist(user_id=user_id, curso_id=curso_id)
        db.session.add(wishlist_item)
        db.session.commit()

        logger.info(f"Curso añadido a wishlist: usuario {user_id}, curso {curso_id}")

        return standardize_response(
            True,
            "Curso añadido a la lista de deseos",
            {"wishlist_item": wishlist_item.to_dict()},
            status_code=201
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al añadir curso a wishlist: {str(e)}", exc_info=True)
        return standardize_response(
            False,
            "Error al añadir el curso a la lista de deseos",
            status_code=500
        )

# Endpoint para eliminar un curso de la lista de deseos
@user_courses_bp.route('/wishlist/<int:curso_id>', methods=['DELETE'])
@jwt_required()
@log_api_call
def remove_from_wishlist(curso_id):
    """Elimina un curso de la lista de deseos del usuario autenticado."""
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()

        # Buscar el elemento en la lista de deseos
        wishlist_item = Wishlist.query.filter_by(
            user_id=user_id,
            curso_id=curso_id
        ).first()

        if not wishlist_item:
            logger.warning(f"Intento de eliminar curso no existente en wishlist: usuario {user_id}, curso {curso_id}")
            return standardize_response(
                False,
                "El curso no está en la lista de deseos",
                status_code=404
            )

        # Eliminar el elemento de la lista de deseos
        db.session.delete(wishlist_item)
        db.session.commit()

        logger.info(f"Curso eliminado de wishlist: usuario {user_id}, curso {curso_id}")

        return standardize_response(
            True,
            "Curso eliminado de la lista de deseos"
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al eliminar curso de wishlist: {str(e)}", exc_info=True)
        return standardize_response(
            False,
            "Error al eliminar el curso de la lista de deseos",
            status_code=500
        )

# Endpoint para obtener el carrito del usuario
@user_courses_bp.route('/cart', methods=['GET'])
@jwt_required()
@log_api_call
def get_cart():
    """Obtiene el carrito de compras del usuario autenticado."""
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()

        # Buscar los cursos en el carrito del usuario
        cart_items = Cart.query.filter_by(user_id=user_id).all()

        # Obtener los detalles de cada curso
        cart = []
        total = 0

        for item in cart_items:
            curso = Curso.query.get(item.curso_id)
            if curso:
                curso_dict = curso.to_dict()
                cart.append({
                    'cart_id': item.id,
                    'curso': curso_dict
                })

                # Sumar al total si el precio está disponible
                if curso.precio:
                    total += float(curso.precio)

        logger.info(f"Carrito obtenido para usuario {user_id}: {len(cart)} cursos")

        return standardize_response(
            True,
            "Carrito obtenido correctamente",
            {
                "cart": cart,
                "total": total,
                "items_count": len(cart)
            }
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al obtener el carrito: {str(e)}", exc_info=True)
        return standardize_response(
            False,
            "Error al obtener el carrito",
            status_code=500
        )

# Endpoint para añadir un curso al carrito
@user_courses_bp.route('/cart', methods=['POST'])
@jwt_required()
@limiter.limit("20/minute")
@log_api_call
def add_to_cart():
    """Añade un curso al carrito de compras del usuario autenticado."""
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()

        # Obtener el ID del curso desde el cuerpo de la solicitud
        data = request.get_json()
        curso_id = data.get('curso_id')

        if not curso_id:
            logger.warning(f"Intento de añadir curso a carrito sin ID de curso: usuario {user_id}")
            return standardize_response(
                False,
                "Se requiere el ID del curso",
                status_code=400
            )

        # Verificar si el curso existe
        curso = Curso.query.get(curso_id)
        if not curso:
            logger.warning(f"Intento de añadir curso inexistente a carrito: usuario {user_id}, curso {curso_id}")
            return standardize_response(
                False,
                "El curso no existe",
                status_code=404
            )

        # Verificar si el curso ya está en el carrito
        existing_item = Cart.query.filter_by(
            user_id=user_id,
            curso_id=curso_id
        ).first()

        if existing_item:
            logger.info(f"Curso ya en carrito: usuario {user_id}, curso {curso_id}")
            return standardize_response(
                False,
                "El curso ya está en el carrito",
                status_code=400
            )

        # Añadir el curso al carrito
        cart_item = Cart(user_id=user_id, curso_id=curso_id)
        db.session.add(cart_item)

        # Si el curso estaba en la lista de deseos, eliminarlo de allí
        wishlist_item = Wishlist.query.filter_by(
            user_id=user_id,
            curso_id=curso_id
        ).first()

        if wishlist_item:
            db.session.delete(wishlist_item)
            logger.info(f"Curso eliminado de wishlist al añadirlo al carrito: usuario {user_id}, curso {curso_id}")

        db.session.commit()

        logger.info(f"Curso añadido al carrito: usuario {user_id}, curso {curso_id}")

        return standardize_response(
            True,
            "Curso añadido al carrito",
            {"cart_item": cart_item.to_dict()},
            status_code=201
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al añadir curso al carrito: {str(e)}", exc_info=True)
        return standardize_response(
            False,
            "Error al añadir el curso al carrito",
            status_code=500
        )

# Endpoint para eliminar un curso del carrito
@user_courses_bp.route('/cart/<int:curso_id>', methods=['DELETE'])
@jwt_required()
@log_api_call
def remove_from_cart(curso_id):
    """Elimina un curso del carrito de compras del usuario autenticado."""
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()

        # Buscar el elemento en el carrito
        cart_item = Cart.query.filter_by(
            user_id=user_id,
            curso_id=curso_id
        ).first()

        if not cart_item:
            logger.warning(f"Intento de eliminar curso no existente en carrito: usuario {user_id}, curso {curso_id}")
            return standardize_response(
                False,
                "El curso no está en el carrito",
                status_code=404
            )

        # Eliminar el elemento del carrito
        db.session.delete(cart_item)
        db.session.commit()

        logger.info(f"Curso eliminado del carrito: usuario {user_id}, curso {curso_id}")

        return standardize_response(
            True,
            "Curso eliminado del carrito"
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al eliminar curso del carrito: {str(e)}", exc_info=True)
        return standardize_response(
            False,
            "Error al eliminar el curso del carrito",
            status_code=500
        )
