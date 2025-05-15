"""
Utilidades para el envío de correos electrónicos.
"""

from flask_mail import Message
from app import mail
from flask import current_app
import logging

# Configurar logger
logger = logging.getLogger(__name__)

def send_verification_email(email, token):
    """
    Envía un correo electrónico de verificación.

    Args:
        email (str): Dirección de correo electrónico del destinatario
        token (str): Token de verificación
    """
    try:
        msg = Message('Verifica tu correo electrónico',
                    recipients=[email])
        link = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/api/auth/verify_email/{token}"
        msg.body = f'Haz clic en el siguiente enlace para verificar tu correo electrónico: {link}'
        msg.html = f'''
        <h1>Verifica tu correo electrónico</h1>
        <p>Haz clic en el siguiente enlace para verificar tu correo electrónico:</p>
        <p><a href="{link}">{link}</a></p>
        <p>Si no solicitaste esta verificación, puedes ignorar este correo.</p>
        '''
        mail.send(msg)
        logger.info(f"Correo de verificación enviado a: {email}")
    except Exception as e:
        logger.error(f"Error al enviar correo de verificación a {email}: {str(e)}", exc_info=True)
        raise

def send_password_reset_email(email, token):
    """
    Envía un correo electrónico para restablecer la contraseña.

    Args:
        email (str): Dirección de correo electrónico del destinatario
        token (str): Token de restablecimiento
    """
    try:
        msg = Message('Restablece tu contraseña',
                    recipients=[email])
        # Usar la URL del frontend para el restablecimiento de contraseña
        link = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/reset-password/{token}"
        msg.body = f'Haz clic en el siguiente enlace para restablecer tu contraseña: {link}'
        msg.html = f'''
        <h1>Restablece tu contraseña</h1>
        <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
        <p><a href="{link}">{link}</a></p>
        <p>Si no solicitaste este restablecimiento, puedes ignorar este correo.</p>
        <p>Este enlace expirará en 1 hora.</p>
        '''
        mail.send(msg)
        logger.info(f"Correo de restablecimiento de contraseña enviado a: {email}")
    except Exception as e:
        logger.error(f"Error al enviar correo de restablecimiento a {email}: {str(e)}", exc_info=True)
        raise

def send_welcome_email(email, name):
    """
    Envía un correo electrónico de bienvenida.

    Args:
        email (str): Dirección de correo electrónico del destinatario
        name (str): Nombre del destinatario
    """
    try:
        msg = Message('¡Bienvenido/a a Akademia Kupula!',
                    recipients=[email])
        msg.body = f'¡Hola {name}! Bienvenido/a a Akademia Kupula. Gracias por registrarte.'
        msg.html = f'''
        <h1>¡Bienvenido/a a Akademia Kupula!</h1>
        <p>¡Hola {name}!</p>
        <p>Gracias por registrarte en Akademia Kupula. Estamos emocionados de tenerte con nosotros.</p>
        <p>Explora nuestros cursos y comienza tu viaje de aprendizaje.</p>
        <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
        <p>¡Saludos!</p>
        <p>El equipo de Akademia Kupula</p>
        '''
        mail.send(msg)
        logger.info(f"Correo de bienvenida enviado a: {email}")
    except Exception as e:
        logger.error(f"Error al enviar correo de bienvenida a {email}: {str(e)}", exc_info=True)
        # No lanzamos la excepción para no interrumpir el flujo si falla el correo de bienvenida
