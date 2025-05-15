import os
import sys
import shutil

# Verificar que estamos en el directorio correcto
if not os.path.exists('app'):
    print("Error: Este script debe ejecutarse desde el directorio raíz del proyecto Flask.")
    sys.exit(1)

# Crear directorios si no existen
os.makedirs('app/models', exist_ok=True)
os.makedirs('app/routes', exist_ok=True)

# Copiar archivos
try:
    # Copiar modelos
    shutil.copy('order_models.py', 'app/models/order_models.py')
    print("✅ Modelos de órdenes copiados correctamente.")
    
    # Copiar rutas
    shutil.copy('payment_routes.py', 'app/routes/payment_routes.py')
    print("✅ Rutas de pagos copiadas correctamente.")
    
except Exception as e:
    print(f"❌ Error al copiar archivos: {str(e)}")
    sys.exit(1)

# Instrucciones para el usuario
print("\n" + "="*80)
print("CONFIGURACIÓN DEL MÓDULO DE PAGOS")
print("="*80)
print("\nPara completar la configuración del módulo de pagos, sigue estos pasos:")

print("\n1. Instala la biblioteca de Stripe:")
print("   pip install stripe")

print("\n2. Registra el blueprint en app/__init__.py:")
print("   # Registrar blueprint de pagos")
print("   from app.routes.payment_routes import payment_bp")
print("   app.register_blueprint(payment_bp, url_prefix='/api/payments')")

print("\n3. Configura las variables de entorno para Stripe:")
print("   export STRIPE_SECRET_KEY='sk_test_TU_CLAVE_SECRETA_DE_STRIPE'")
print("   export STRIPE_WEBHOOK_SECRET='whsec_TU_CLAVE_DE_WEBHOOK_DE_STRIPE'")
print("   (En Windows, usa 'set' en lugar de 'export')")

print("\n4. Crea las tablas en la base de datos:")
print("   Ejecuta el siguiente código en una consola de Python:")
print("   from app import app, db")
print("   from app.models.order_models import Order, OrderItem")
print("   with app.app_context():")
print("       db.create_all()")

print("\n5. Configura el webhook en el dashboard de Stripe:")
print("   a. Ve a https://dashboard.stripe.com/webhooks")
print("   b. Haz clic en 'Añadir endpoint'")
print("   c. Introduce la URL: https://tu-dominio.com/api/payments/webhook")
print("   d. Selecciona los eventos: checkout.session.completed")
print("   e. Guarda y copia la clave de firma del webhook")

print("\n6. Reinicia el servidor Flask:")
print("   python run.py")

print("\n" + "="*80)
print("NOTA: Para pruebas locales, puedes usar Stripe CLI para reenviar eventos de webhook:")
print("https://stripe.com/docs/stripe-cli")
print("="*80)

print("\n¡Configuración completada! El módulo de pagos está listo para usar.")
