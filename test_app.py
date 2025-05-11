"""
Script para probar la inicialización de la aplicación Flask.
"""

from app import create_app

print("Iniciando prueba de la aplicación...")
try:
    app = create_app()
    print("¡La aplicación se ha inicializado correctamente!")
    print(f"Configuración de la base de datos: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("La aplicación está lista para ejecutarse.")
except Exception as e:
    print(f"Error al inicializar la aplicación: {str(e)}")
    import traceback
    traceback.print_exc()
