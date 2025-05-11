# Rutas para la lista de deseos y el carrito
# Crea un nuevo archivo en tu carpeta de rutas (por ejemplo, api/user_courses.py)

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Course, Wishlist, Cart
from sqlalchemy.exc import SQLAlchemyError

# Ajusta la importación según la estructura de tu proyecto
# Por ejemplo, podría ser from models import db, User, Course, Wishlist, Cart

user_courses = Blueprint('user_courses', __name__)

# Endpoint para obtener la lista de deseos del usuario
@user_courses.route('/wishlist', methods=['GET'])
@jwt_required()
def get_wishlist():
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Buscar los cursos en la lista de deseos del usuario
        wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
        
        # Obtener los detalles de cada curso
        wishlist = []
        for item in wishlist_items:
            course = Course.query.get(item.course_id)
            if course:
                wishlist.append({
                    'id': course.id,
                    'title': course.title,
                    'price': float(course.price),
                    'image': course.image_url
                })
        
        return jsonify({
            'success': True,
            'wishlist': wishlist
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error al obtener la lista de deseos',
            'error': str(e)
        }), 500

# Endpoint para añadir un curso a la lista de deseos
@user_courses.route('/wishlist', methods=['POST'])
@jwt_required()
def add_to_wishlist():
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Obtener el ID del curso desde el cuerpo de la solicitud
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({
                'success': False,
                'message': 'Se requiere el ID del curso'
            }), 400
        
        # Verificar si el curso existe
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'El curso no existe'
            }), 404
        
        # Verificar si el curso ya está en la lista de deseos
        existing_item = Wishlist.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if existing_item:
            return jsonify({
                'success': False,
                'message': 'El curso ya está en la lista de deseos'
            }), 400
        
        # Añadir el curso a la lista de deseos
        wishlist_item = Wishlist(user_id=user_id, course_id=course_id)
        db.session.add(wishlist_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Curso añadido a la lista de deseos'
        }), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error al añadir el curso a la lista de deseos',
            'error': str(e)
        }), 500

# Endpoint para eliminar un curso de la lista de deseos
@user_courses.route('/wishlist/<int:course_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(course_id):
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Buscar el elemento en la lista de deseos
        wishlist_item = Wishlist.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if not wishlist_item:
            return jsonify({
                'success': False,
                'message': 'El curso no está en la lista de deseos'
            }), 404
        
        # Eliminar el elemento de la lista de deseos
        db.session.delete(wishlist_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Curso eliminado de la lista de deseos'
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error al eliminar el curso de la lista de deseos',
            'error': str(e)
        }), 500

# Endpoint para obtener el carrito del usuario
@user_courses.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Buscar los cursos en el carrito del usuario
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        
        # Obtener los detalles de cada curso
        cart = []
        for item in cart_items:
            course = Course.query.get(item.course_id)
            if course:
                cart.append({
                    'id': course.id,
                    'title': course.title,
                    'price': float(course.price),
                    'image': course.image_url
                })
        
        return jsonify({
            'success': True,
            'cart': cart
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error al obtener el carrito',
            'error': str(e)
        }), 500

# Endpoint para añadir un curso al carrito
@user_courses.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Obtener el ID del curso desde el cuerpo de la solicitud
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({
                'success': False,
                'message': 'Se requiere el ID del curso'
            }), 400
        
        # Verificar si el curso existe
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'El curso no existe'
            }), 404
        
        # Verificar si el curso ya está en el carrito
        existing_item = Cart.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if existing_item:
            return jsonify({
                'success': False,
                'message': 'El curso ya está en el carrito'
            }), 400
        
        # Añadir el curso al carrito
        cart_item = Cart(user_id=user_id, course_id=course_id)
        db.session.add(cart_item)
        db.session.commit()
        
        # Si el curso estaba en la lista de deseos, eliminarlo de allí
        wishlist_item = Wishlist.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if wishlist_item:
            db.session.delete(wishlist_item)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Curso añadido al carrito'
        }), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error al añadir el curso al carrito',
            'error': str(e)
        }), 500

# Endpoint para eliminar un curso del carrito
@user_courses.route('/cart/<int:course_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(course_id):
    try:
        # Obtener el ID del usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Buscar el elemento en el carrito
        cart_item = Cart.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if not cart_item:
            return jsonify({
                'success': False,
                'message': 'El curso no está en el carrito'
            }), 404
        
        # Eliminar el elemento del carrito
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Curso eliminado del carrito'
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error al eliminar el curso del carrito',
            'error': str(e)
        }), 500
