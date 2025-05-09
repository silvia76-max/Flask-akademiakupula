from flask import Blueprint, request, jsonify
from app.models.contacto import Contacto
from app import db
import re

# Crea el Blueprint
contacto_bp = Blueprint('contacto', __name__)

@contacto_bp.route('', methods=['POST'])
def crear_contacto():
    """
    Crea un nuevo mensaje de contacto
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Extraer datos del cuerpo de la solicitud
        data = request.get_json()

        # Validar que todos los campos obligatorios estén presentes
        required_fields = ['nombre', 'email', 'mensaje']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "Faltan campos obligatorios (nombre, email, mensaje)",
                "data": None
            }), 400

        # Validar formato de email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return jsonify({
                "success": False,
                "message": "Formato de email inválido",
                "data": None
            }), 400

        # Validar longitud del mensaje
        if len(data['mensaje']) < 10:
            return jsonify({
                "success": False,
                "message": "El mensaje debe tener al menos 10 caracteres",
                "data": None
            }), 400

        # Crear un nuevo registro en la base de datos
        nuevo_contacto = Contacto(
            nombre=data['nombre'],
            email=data['email'],
            mensaje=data['mensaje']
        )
        db.session.add(nuevo_contacto)
        db.session.commit()

        # Devolver una respuesta exitosa
        return jsonify({
            "success": True,
            "message": "Mensaje recibido correctamente",
            "data": {
                "id": nuevo_contacto.id,
                "nombre": nuevo_contacto.nombre,
                "email": nuevo_contacto.email,
                "mensaje": nuevo_contacto.mensaje,
                "fecha_creacion": nuevo_contacto.fecha_creacion.isoformat()
            }
        }), 201

    except Exception as e:
        # Revertir la transacción en caso de error
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al procesar el mensaje: {str(e)}",
            "data": None
        }), 500

@contacto_bp.route('', methods=['GET'])
def obtener_mensajes():
    """
    Obtiene todos los mensajes de contacto (solo para administradores en una implementación real)
    """
    try:
        mensajes = Contacto.query.order_by(Contacto.fecha_creacion.desc()).all()
        resultado = []

        for mensaje in mensajes:
            resultado.append({
                "id": mensaje.id,
                "nombre": mensaje.nombre,
                "email": mensaje.email,
                "mensaje": mensaje.mensaje,
                "fecha_creacion": mensaje.fecha_creacion.isoformat()
            })

        return jsonify({
            "success": True,
            "message": "Mensajes obtenidos correctamente",
            "data": resultado
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener mensajes: {str(e)}",
            "data": None
        }), 500