"""
Rutas para la gestión de cursos desde el panel de administración.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app import db
from app.models.curso import Curso
from app.utils.auth_middleware import admin_required
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear blueprint
admin_courses_bp = Blueprint('admin_courses', __name__)

@admin_courses_bp.route('/courses', methods=['GET'])
@jwt_required()
@admin_required
def get_courses():
    """Endpoint para obtener todos los cursos"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Obtener cursos paginados
        courses_pagination = Curso.query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Preparar datos de cursos
        courses_data = [course.to_dict() for course in courses_pagination.items]
        
        return jsonify({
            "success": True,
            "message": "Cursos obtenidos correctamente",
            "data": {
                "courses": courses_data,
                "pagination": {
                    "total": courses_pagination.total,
                    "pages": courses_pagination.pages,
                    "page": page,
                    "per_page": per_page,
                    "has_next": courses_pagination.has_next,
                    "has_prev": courses_pagination.has_prev
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener cursos: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error al obtener cursos: {str(e)}",
            "data": None
        }), 500

@admin_courses_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_course(course_id):
    """Endpoint para obtener un curso específico"""
    try:
        course = Curso.query.get_or_404(course_id)
        
        return jsonify({
            "success": True,
            "message": "Curso obtenido correctamente",
            "data": course.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener curso {course_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error al obtener curso: {str(e)}",
            "data": None
        }), 500

@admin_courses_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_course(course_id):
    """Endpoint para actualizar un curso"""
    try:
        course = Curso.query.get_or_404(course_id)
        data = request.get_json()
        
        # Actualizar campos del curso
        if 'title' in data:
            course.title = data['title']
        if 'description' in data:
            course.description = data['description']
        if 'price' in data:
            course.price = data['price']
        if 'level' in data:
            course.level = data['level']
        if 'duration' in data:
            course.duration = data['duration']
        if 'image_url' in data:
            course.image_url = data['image_url']
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Curso actualizado correctamente",
            "data": course.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar curso {course_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error al actualizar curso: {str(e)}",
            "data": None
        }), 500

@admin_courses_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_course(course_id):
    """Endpoint para eliminar un curso"""
    try:
        course = Curso.query.get_or_404(course_id)
        
        # Eliminar curso
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Curso eliminado correctamente",
            "data": None
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar curso {course_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error al eliminar curso: {str(e)}",
            "data": None
        }), 500

@admin_courses_bp.route('/courses', methods=['POST'])
@jwt_required()
@admin_required
def create_course():
    """Endpoint para crear un nuevo curso"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['title', 'description', 'price', 'level', 'duration']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"El campo '{field}' es requerido",
                    "data": None
                }), 400
        
        # Crear nuevo curso
        new_course = Curso(
            title=data['title'],
            description=data['description'],
            price=data['price'],
            level=data['level'],
            duration=data['duration'],
            image_url=data.get('image_url', '')
        )
        
        # Guardar en la base de datos
        db.session.add(new_course)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Curso creado correctamente",
            "data": new_course.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear curso: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error al crear curso: {str(e)}",
            "data": None
        }), 500