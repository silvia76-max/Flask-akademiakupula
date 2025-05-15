from flask import Blueprint, jsonify, request, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import os
from app import db
from app.models.user import User
from app.models.curso import Curso
from app.models.order import Order, OrderItem
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

# Configurar Stripe con la clave secreta
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51NXwqnLZIKXBHZxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

@payment_bp.route('/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """
    Crea una sesión de checkout de Stripe para un curso.

    Requiere autenticación JWT.

    Request body:
    {
        "courseId": "curso-de-maquillaje-profesional"
    }

    Returns:
        JSON con el ID de la sesión de Stripe
    """
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado",
                "data": None
            }), 404

        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()

        if not data or 'courseId' not in data:
            return jsonify({
                "success": False,
                "message": "Datos incompletos. Se requiere courseId",
                "data": None
            }), 400

        course_id = data['courseId']

        # Buscar el curso en la base de datos
        course = Curso.query.filter_by(id=course_id).first()

        if not course:
            return jsonify({
                "success": False,
                "message": f"Curso con ID {course_id} no encontrado",
                "data": None
            }), 404

        # Crear la sesión de checkout de Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': course.title,
                            'description': course.description,
                            'images': [course.image_url] if course.image_url else [],
                        },
                        'unit_amount': int(course.price * 100),  # Convertir a centavos
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'user_id': user_id,
                'course_id': course_id,
            },
            mode='payment',
            success_url=f"{request.host_url.rstrip('/')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url.rstrip('/')}/payment/cancel",
        )

        return jsonify({
            "success": True,
            "message": "Sesión de checkout creada correctamente",
            "data": {
                "sessionId": checkout_session.id
            }
        }), 200
    except stripe.error.StripeError as e:
        return jsonify({
            "success": False,
            "message": f"Error de Stripe: {str(e)}",
            "data": None
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al crear la sesión de checkout: {str(e)}",
            "data": None
        }), 500

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook para recibir eventos de Stripe.

    Este endpoint debe configurarse en el dashboard de Stripe.

    Returns:
        Respuesta HTTP 200 si el evento se procesa correctamente
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({"success": False, "message": "Payload inválido"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({"success": False, "message": "Firma inválida"}), 400

    # Manejar el evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Extraer metadatos
        user_id = session.get('metadata', {}).get('user_id')
        course_id = session.get('metadata', {}).get('course_id')

        if user_id and course_id:
            try:
                # Crear un nuevo pedido
                order = Order(
                    user_id=user_id,
                    total_amount=session.get('amount_total', 0) / 100,  # Convertir de centavos a euros
                    payment_status='completed',
                    payment_id=session.get('id'),
                    payment_method='stripe',
                    created_at=datetime.now()
                )
                db.session.add(order)
                db.session.flush()  # Para obtener el ID del pedido

                # Crear un elemento de pedido para el curso
                order_item = OrderItem(
                    order_id=order.id,
                    course_id=course_id,
                    price=session.get('amount_total', 0) / 100,
                    quantity=1
                )
                db.session.add(order_item)

                # Guardar en la base de datos
                db.session.commit()

                return jsonify({"success": True, "message": "Pago procesado correctamente"}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"success": False, "message": f"Error al procesar el pago: {str(e)}"}), 500

    return jsonify({"success": True, "message": "Evento recibido"}), 200

@payment_bp.route('/check-payment-status/<session_id>', methods=['GET'])
@jwt_required()
def check_payment_status(session_id):
    """
    Verifica el estado de un pago.

    Requiere autenticación JWT.

    Args:
        session_id: ID de la sesión de Stripe

    Returns:
        JSON con el estado del pago
    """
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()

        # Buscar el pedido en la base de datos
        order = Order.query.filter_by(payment_id=session_id).first()

        if not order:
            # Si no encontramos el pedido en la base de datos, verificamos con Stripe
            try:
                session = stripe.checkout.Session.retrieve(session_id)

                if session.payment_status == 'paid':
                    # El pago se completó, pero no se registró en nuestra base de datos
                    # Esto podría suceder si el webhook falló
                    course_id = session.metadata.get('course_id')
                    course = Curso.query.filter_by(id=course_id).first()

                    return jsonify({
                        "success": True,
                        "message": "Pago completado (verificado con Stripe)",
                        "data": {
                            "paymentStatus": "completed",
                            "courseId": course_id,
                            "courseName": course.title if course else "Curso desconocido",
                            "amount": session.amount_total / 100,
                            "paymentDate": datetime.now().isoformat(),
                            "orderId": f"STRIPE-{session_id[:8]}"
                        }
                    }), 200
                else:
                    return jsonify({
                        "success": False,
                        "message": "Pago no completado",
                        "data": {
                            "paymentStatus": session.payment_status
                        }
                    }), 200
            except stripe.error.StripeError as e:
                return jsonify({
                    "success": False,
                    "message": f"Error al verificar el pago con Stripe: {str(e)}",
                    "data": None
                }), 500

        # Verificar que el pedido pertenece al usuario autenticado
        if str(order.user_id) != str(user_id):
            return jsonify({
                "success": False,
                "message": "No tienes permiso para ver este pedido",
                "data": None
            }), 403

        # Obtener el primer elemento del pedido (asumimos que solo hay uno)
        order_item = OrderItem.query.filter_by(order_id=order.id).first()

        if not order_item:
            return jsonify({
                "success": False,
                "message": "No se encontraron detalles del pedido",
                "data": None
            }), 404

        # Obtener información del curso
        course = Curso.query.filter_by(id=order_item.course_id).first()

        return jsonify({
            "success": True,
            "message": "Estado del pago obtenido correctamente",
            "data": {
                "paymentStatus": order.payment_status,
                "courseId": order_item.course_id,
                "courseName": course.title if course else "Curso desconocido",
                "amount": order.total_amount,
                "paymentDate": order.created_at.isoformat(),
                "orderId": f"ORD-{order.id}"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al verificar el estado del pago: {str(e)}",
            "data": None
        }), 500

@payment_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """
    Obtiene el historial de pagos del usuario.

    Requiere autenticación JWT.

    Returns:
        JSON con el historial de pagos
    """
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()

        # Buscar los pedidos del usuario
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

        # Preparar la respuesta
        payment_history = []

        for order in orders:
            # Obtener los elementos del pedido
            order_items = OrderItem.query.filter_by(order_id=order.id).all()

            # Preparar los elementos del pedido
            items = []

            for item in order_items:
                # Obtener información del curso
                course = Curso.query.filter_by(id=item.course_id).first()

                items.append({
                    "courseId": item.course_id,
                    "courseName": course.title if course else "Curso desconocido",
                    "price": item.price,
                    "quantity": item.quantity
                })

            payment_history.append({
                "orderId": order.id,
                "totalAmount": order.total_amount,
                "paymentStatus": order.payment_status,
                "paymentMethod": order.payment_method,
                "paymentId": order.payment_id,
                "createdAt": order.created_at.isoformat(),
                "items": items
            })

        return jsonify({
            "success": True,
            "message": "Historial de pagos obtenido correctamente",
            "data": payment_history
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener el historial de pagos: {str(e)}",
            "data": None
        }), 500
