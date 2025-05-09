from flask import Blueprint, jsonify, request
from app.models.curso import Curso
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

cursos_bp = Blueprint('cursos', __name__)

@cursos_bp.route('/', methods=['GET'])
def get_cursos():
    """
    Obtiene todos los cursos disponibles
    """
    try:
        cursos = Curso.query.all()
        resultado = []
        for curso in cursos:
            resultado.append({
                'id': curso.id,
                'titulo': curso.titulo,
                'descripcion': curso.descripcion,
                'duracion': curso.duracion,
                'precio': curso.precio
            })
        return jsonify({
            "success": True,
            "message": "Cursos obtenidos correctamente",
            "data": resultado
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener cursos: {str(e)}",
            "data": None
        }), 500

@cursos_bp.route('/<int:curso_id>', methods=['GET'])
def get_curso(curso_id):
    """
    Obtiene un curso específico por su ID
    """
    try:
        curso = Curso.query.get(curso_id)
        if not curso:
            return jsonify({
                "success": False,
                "message": "Curso no encontrado",
                "data": None
            }), 404

        return jsonify({
            "success": True,
            "message": "Curso obtenido correctamente",
            "data": {
                'id': curso.id,
                'titulo': curso.titulo,
                'descripcion': curso.descripcion,
                'duracion': curso.duracion,
                'precio': curso.precio
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener curso: {str(e)}",
            "data": None
        }), 500

@cursos_bp.route('/', methods=['POST'])
@jwt_required()
def crear_curso():
    """
    Crea un nuevo curso (requiere autenticación)
    """
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data or 'titulo' not in data or 'descripcion' not in data:
            return jsonify({
                "success": False,
                "message": "Título y descripción son requeridos",
                "data": None
            }), 400

        nuevo_curso = Curso(
            titulo=data['titulo'],
            descripcion=data['descripcion'],
            duracion=data.get('duracion'),
            precio=data.get('precio')
        )

        db.session.add(nuevo_curso)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Curso creado correctamente",
            "data": {
                'id': nuevo_curso.id,
                'titulo': nuevo_curso.titulo,
                'descripcion': nuevo_curso.descripcion,
                'duracion': nuevo_curso.duracion,
                'precio': nuevo_curso.precio
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al crear curso: {str(e)}",
            "data": None
        }), 500

@cursos_bp.route('/<int:curso_id>', methods=['PUT'])
@jwt_required()
def actualizar_curso(curso_id):
    """
    Actualiza un curso existente (requiere autenticación)
    """
    try:
        curso = Curso.query.get(curso_id)
        if not curso:
            return jsonify({
                "success": False,
                "message": "Curso no encontrado",
                "data": None
            }), 404

        data = request.get_json()

        if 'titulo' in data:
            curso.titulo = data['titulo']
        if 'descripcion' in data:
            curso.descripcion = data['descripcion']
        if 'duracion' in data:
            curso.duracion = data['duracion']
        if 'precio' in data:
            curso.precio = data['precio']

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Curso actualizado correctamente",
            "data": {
                'id': curso.id,
                'titulo': curso.titulo,
                'descripcion': curso.descripcion,
                'duracion': curso.duracion,
                'precio': curso.precio
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al actualizar curso: {str(e)}",
            "data": None
        }), 500

@cursos_bp.route('/<int:curso_id>', methods=['DELETE'])
@jwt_required()
def eliminar_curso(curso_id):
    """
    Elimina un curso existente (requiere autenticación)
    """
    try:
        curso = Curso.query.get(curso_id)
        if not curso:
            return jsonify({
                "success": False,
                "message": "Curso no encontrado",
                "data": None
            }), 404

        db.session.delete(curso)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Curso eliminado correctamente",
            "data": None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al eliminar curso: {str(e)}",
            "data": None
        }), 500
