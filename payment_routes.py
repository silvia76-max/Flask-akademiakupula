import os
import stripe
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order_models import Order, OrderItem
from app.models.course_models import Course
from app.models.user_models import User

# Crear el blueprint
payment_bp = Blueprint('payment', __name__)

# Configurar Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_TU_CLAVE_SECRETA_DE_STRIPE')
webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_TU_CLAVE_DE_WEBHOOK_DE_STRIPE')

@payment_bp.route('/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Crea una sesión de checkout de Stripe"""
    try:
        # Obtener el ID del usuario actual
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        # Obtener datos del request
        data = request.get_json()
        course_id = data.get('courseId')
        
        if not course_id:
            return jsonify({'message': 'ID del curso no proporcionado'}), 400
        
        # Buscar el curso
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'message': 'Curso no encontrado'}), 404
        
        # Crear la sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': course.title,
                            'description': course.description[:255] if course.description else '',
                            'images': [course.image_url] if course.image_url else [],
                        },
                        'unit_amount': int(course.price * 100),  # Stripe usa centavos
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f"{request.host_url.rstrip('/')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url.rstrip('/')}/payment/cancel",
            client_reference_id=str(current_user_id),
            metadata={
                'course_id': course_id,
                'user_id': current_user_id
            }
        )
        
        # Crear la orden en la base de datos
        order = Order(
            user_id=current_user_id,
            status='pending',
            total_amount=course.price,
            checkout_session_id=checkout_session.id
        )
        db.session.add(order)
        db.session.flush()  # Para obtener el ID de la orden
        
        # Crear el item de la orden
        order_item = OrderItem(
            order_id=order.id,
            course_id=course_id,
            price=course.price
        )
        db.session.add(order_item)
        db.session.commit()
        
        return jsonify({
            'sessionId': checkout_session.id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al crear la sesión de checkout: {str(e)}")
        db.session.rollback()
        return jsonify({'message': f'Error al crear la sesión de checkout: {str(e)}'}), 500

@payment_bp.route('/check-payment-status/<session_id>', methods=['GET'])
@jwt_required()
def check_payment_status(session_id):
    """Verifica el estado de un pago"""
    try:
        # Obtener el ID del usuario actual
        current_user_id = get_jwt_identity()
        
        # Buscar la orden
        order = Order.query.filter_by(checkout_session_id=session_id).first()
        
        if not order:
            return jsonify({'message': 'Orden no encontrada'}), 404
        
        # Verificar que la orden pertenece al usuario
        if order.user_id != current_user_id:
            return jsonify({'message': 'No tienes permiso para ver esta orden'}), 403
        
        # Obtener la sesión de Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Actualizar el estado de la orden si es necesario
        if checkout_session.payment_status == 'paid' and order.status != 'completed':
            order.status = 'completed'
            order.payment_intent_id = checkout_session.payment_intent
            db.session.commit()
        
        # Obtener información del curso
        order_item = OrderItem.query.filter_by(order_id=order.id).first()
        course = Course.query.get(order_item.course_id) if order_item else None
        
        return jsonify({
            'orderId': order.id,
            'status': order.status,
            'amount': order.total_amount,
            'paymentDate': order.updated_at.isoformat() if order.updated_at else None,
            'courseId': order_item.course_id if order_item else None,
            'courseName': course.title if course else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al verificar el estado del pago: {str(e)}")
        return jsonify({'message': f'Error al verificar el estado del pago: {str(e)}'}), 500

@payment_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Obtiene el historial de pagos del usuario"""
    try:
        # Obtener el ID del usuario actual
        current_user_id = get_jwt_identity()
        
        # Buscar las órdenes del usuario
        orders = Order.query.filter_by(user_id=current_user_id).order_by(Order.created_at.desc()).all()
        
        # Formatear la respuesta
        orders_data = []
        for order in orders:
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            courses = []
            for item in order_items:
                course = Course.query.get(item.course_id)
                if course:
                    courses.append({
                        'id': course.id,
                        'title': course.title,
                        'price': item.price
                    })
            
            orders_data.append({
                'id': order.id,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'courses': courses
            })
        
        return jsonify({
            'data': orders_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener el historial de pagos: {str(e)}")
        return jsonify({'message': f'Error al obtener el historial de pagos: {str(e)}'}), 500

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    """Recibe eventos de Stripe"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        current_app.logger.error(f"Payload inválido: {str(e)}")
        return jsonify({'message': 'Payload inválido'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        current_app.logger.error(f"Firma inválida: {str(e)}")
        return jsonify({'message': 'Firma inválida'}), 400
    
    # Manejar el evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Actualizar la orden
        order = Order.query.filter_by(checkout_session_id=session.id).first()
        if order:
            order.status = 'completed'
            order.payment_intent_id = session.payment_intent
            db.session.commit()
            
            # Aquí podrías añadir lógica adicional, como:
            # - Enviar un correo de confirmación
            # - Dar acceso al curso
            # - Actualizar inventario
            # - etc.
    
    return jsonify({'status': 'success'}), 200
