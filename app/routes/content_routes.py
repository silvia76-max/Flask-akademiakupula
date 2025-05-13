from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.content import Content
from app.models.user import User
from app import db, cache
from app.utils.auth_middleware import admin_required
import re
from slugify import slugify

content_bp = Blueprint('content', __name__)

@content_bp.route('/', methods=['GET'])
def get_content_list():
    """Endpoint para obtener lista de contenidos públicos."""
    try:
        # Parámetros de filtrado
        content_type = request.args.get('type')
        featured = request.args.get('featured', '').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)
        
        # Construir la consulta
        query = Content.query.filter_by(published=True)
        
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        if featured:
            query = query.filter_by(featured=True)
        
        # Obtener resultados
        content_list = query.order_by(Content.created_at.desc()).limit(limit).all()
        content_data = [item.to_dict() for item in content_list]
        
        return jsonify({
            "success": True,
            "message": "Contenido obtenido correctamente",
            "data": content_data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener contenido: {str(e)}",
            "data": None
        }), 500

@content_bp.route('/<string:slug>', methods=['GET'])
def get_content_by_slug(slug):
    """Endpoint para obtener un contenido específico por su slug."""
    try:
        content = Content.get_by_slug(slug)
        
        if not content:
            return jsonify({
                "success": False,
                "message": "Contenido no encontrado",
                "data": None
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Contenido obtenido correctamente",
            "data": content.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener contenido: {str(e)}",
            "data": None
        }), 500

@content_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_content():
    """Endpoint para crear nuevo contenido (solo administradores)."""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['title', 'content', 'content_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False,
                    "message": f"El campo '{field}' es requerido",
                    "data": None
                }), 400
        
        # Generar slug si no se proporciona
        if 'slug' not in data or not data['slug']:
            data['slug'] = slugify(data['title'])
        
        # Verificar si el slug ya existe
        existing_content = Content.query.filter_by(slug=data['slug']).first()
        if existing_content:
            return jsonify({
                "success": False,
                "message": f"Ya existe contenido con el slug '{data['slug']}'",
                "data": None
            }), 400
        
        # Obtener el usuario actual como autor
        current_user_id = get_jwt_identity()
        
        # Crear nuevo contenido
        new_content = Content(
            title=data['title'],
            slug=data['slug'],
            content=data['content'],
            summary=data.get('summary'),
            image_url=data.get('image_url'),
            published=data.get('published', True),
            featured=data.get('featured', False),
            content_type=data['content_type'],
            author_id=current_user_id
        )
        
        db.session.add(new_content)
        db.session.commit()
        
        # Invalidar caché
        cache.delete_memoized(Content.get_by_slug, Content, data['slug'])
        cache.delete_memoized(Content.get_featured, Content)
        cache.delete_memoized(Content.get_latest, Content)
        
        return jsonify({
            "success": True,
            "message": "Contenido creado correctamente",
            "data": new_content.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al crear contenido: {str(e)}",
            "data": None
        }), 500

@content_bp.route('/<int:content_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_content(content_id):
    """Endpoint para actualizar contenido existente (solo administradores)."""
    try:
        content = Content.query.get_or_404(content_id)
        data = request.get_json()
        
        # Actualizar campos
        if 'title' in data:
            content.title = data['title']
        if 'content' in data:
            content.content = data['content']
        if 'summary' in data:
            content.summary = data['summary']
        if 'image_url' in data:
            content.image_url = data['image_url']
        if 'published' in data:
            content.published = data['published']
        if 'featured' in data:
            content.featured = data['featured']
        if 'content_type' in data:
            content.content_type = data['content_type']
        
        # Actualizar slug si se proporciona
        old_slug = content.slug
        if 'slug' in data and data['slug'] != old_slug:
            # Verificar si el nuevo slug ya existe
            existing_content = Content.query.filter_by(slug=data['slug']).first()
            if existing_content and existing_content.id != content_id:
                return jsonify({
                    "success": False,
                    "message": f"Ya existe contenido con el slug '{data['slug']}'",
                    "data": None
                }), 400
            content.slug = data['slug']
        
        db.session.commit()
        
        # Invalidar caché
        cache.delete_memoized(Content.get_by_slug, Content, old_slug)
        cache.delete_memoized(Content.get_by_slug, Content, content.slug)
        cache.delete_memoized(Content.get_featured, Content)
        cache.delete_memoized(Content.get_latest, Content)
        
        return jsonify({
            "success": True,
            "message": "Contenido actualizado correctamente",
            "data": content.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al actualizar contenido: {str(e)}",
            "data": None
        }), 500

@content_bp.route('/<int:content_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_content(content_id):
    """Endpoint para eliminar contenido (solo administradores)."""
    try:
        content = Content.query.get_or_404(content_id)
        
        # Guardar slug para invalidar caché después
        slug = content.slug
        
        db.session.delete(content)
        db.session.commit()
        
        # Invalidar caché
        cache.delete_memoized(Content.get_by_slug, Content, slug)
        cache.delete_memoized(Content.get_featured, Content)
        cache.delete_memoized(Content.get_latest, Content)
        
        return jsonify({
            "success": True,
            "message": "Contenido eliminado correctamente",
            "data": None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al eliminar contenido: {str(e)}",
            "data": None
        }), 500
