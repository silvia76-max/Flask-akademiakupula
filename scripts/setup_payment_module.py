"""
Script para configurar el módulo de pagos.
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scripts/setup_payment_module.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando configuración del módulo de pagos")

        # Añadir el directorio del proyecto al path
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, project_dir)

        # Verificar que estamos en el directorio correcto
        if not os.path.exists(os.path.join(project_dir, 'app')):
            logger.error("Error: Este script debe ejecutarse desde el directorio raíz del proyecto Flask.")
            return False

        # Verificar que los archivos necesarios existen
        if not os.path.exists(os.path.join(project_dir, 'app/models/order.py')):
            logger.error("Error: No se encontró el archivo app/models/order.py")
            return False

        if not os.path.exists(os.path.join(project_dir, 'app/routes/payment_routes.py')):
            logger.error("Error: No se encontró el archivo app/routes/payment_routes.py")
            return False

        # Verificar que Stripe está instalado
        try:
            import stripe
            logger.info(f"Stripe instalado correctamente")
        except ImportError:
            logger.warning("Stripe no está instalado. Instalando...")
            os.system(f"{sys.executable} -m pip install stripe")
            try:
                import stripe
                logger.info(f"Stripe instalado correctamente")
            except ImportError:
                logger.error("Error: No se pudo instalar Stripe. Instálalo manualmente con 'pip install stripe'")
                return False

        # Crear las tablas en la base de datos
        logger.info("Creando tablas en la base de datos...")

        from app import create_app
        from app import db

        app = create_app()

        with app.app_context():
            from app.models.order import Order, OrderItem

            # Verificar si las tablas ya existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)

            tables = inspector.get_table_names()
            if 'orders' in tables and 'order_items' in tables:
                logger.info("Las tablas 'orders' y 'order_items' ya existen en la base de datos.")
            else:
                # Crear las tablas
                db.create_all()
                logger.info("Tablas creadas correctamente.")

        # Mostrar instrucciones para configurar Stripe
        print("\n" + "="*80)
        print("CONFIGURACIÓN DEL MÓDULO DE PAGOS")
        print("="*80)

        print("\n1. Configura las variables de entorno para Stripe:")
        print("   export STRIPE_SECRET_KEY='sk_test_TU_CLAVE_SECRETA_DE_STRIPE'")
        print("   export STRIPE_WEBHOOK_SECRET='whsec_TU_CLAVE_DE_WEBHOOK_DE_STRIPE'")
        print("   (En Windows, usa 'set' en lugar de 'export')")

        print("\n2. Configura el webhook en el dashboard de Stripe:")
        print("   a. Ve a https://dashboard.stripe.com/webhooks")
        print("   b. Haz clic en 'Añadir endpoint'")
        print("   c. Introduce la URL: https://tu-dominio.com/api/payment/webhook")
        print("   d. Selecciona los eventos: checkout.session.completed")
        print("   e. Guarda y copia la clave de firma del webhook")

        print("\n3. Para pruebas locales, puedes usar Stripe CLI para reenviar eventos de webhook:")
        print("   https://stripe.com/docs/stripe-cli")

        print("\n" + "="*80)
        print("¡Configuración completada! El módulo de pagos está listo para usar.")
        print("="*80)

        logger.info("Configuración del módulo de pagos completada con éxito.")
        return True

    except Exception as e:
        logger.error(f"Error durante la configuración: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
