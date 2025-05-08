from flask import Blueprint, request, jsonify, url_for
from app.models import User
from app import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import Config
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__)
s = URLSafeTimedSerializer(Config.SECRET_KEY)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name')
    postal_code = data.get('postal_code')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email ya registrado"}), 400

    user = User(full_name=full_name, postal_code=postal_code, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = s.dumps(email, salt='email-confirm')
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    msg = Message('Confirma tu cuenta', sender=Config.MAIL_DEFAULT_SENDER, recipients=[email])
    msg.body = f'Por favor confirma tu cuenta haciendo click aquí: {confirm_url}'
    mail.send(msg)

    return jsonify({"message": "Registro exitoso. Revisa tu email para confirmar tu cuenta."}), 201

@auth.route('/confirm-email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return jsonify({"message": "El enlace de confirmación ha expirado."}), 400
    except BadSignature:
        return jsonify({"message": "El enlace de confirmación es inválido."}), 400

    user = User.query.filter_by(email=email).first_or_404()

    if user.is_confirmed:
        return jsonify({"message": "Cuenta ya confirmada."}), 200

    user.is_confirmed = True
    db.session.commit()

    return jsonify({"message": "Cuenta confirmada correctamente."}), 200

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Credenciales inválidas"}), 401

    if not user.check_password(password):
        return jsonify({"message": "Credenciales inválidas"}), 401

    if not user.is_confirmed:
        return jsonify({"message": "Confirma tu email antes de iniciar sesión"}), 401


    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "postal_code": user.postal_code
        }
    }), 200

@auth.route('/profile', methods=['GET'])
@jwt_required()  
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    return jsonify({
        "full_name": user.full_name,
        "email": user.email,
        "postal_code": user.postal_code,
        "message": "Bienvenido a tu perfil"
    }), 200

@auth.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Sesión cerrada correctamente"}), 200