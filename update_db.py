"""
Script simple para actualizar la base de datos.
Ajusta las importaciones según la estructura de tu proyecto.
"""

# Ajusta estas importaciones según la estructura de tu proyecto
try:
    from run import app
    from models import db
    
    print("Importaciones exitosas.")
    
    with app.app_context():
        db.create_all()
        print("Base de datos actualizada con éxito.")
        print("Se han creado las tablas si no existían previamente.")
        
except ImportError as e:
    print(f"Error de importación: {e}")
    print("\nAjusta las importaciones según la estructura de tu proyecto.")
    print("Por ejemplo, si tu aplicación está en un paquete 'app':")
    print("from app import app")
    print("from app.models import db")
    
except Exception as e:
    print(f"Error al actualizar la base de datos: {e}")
