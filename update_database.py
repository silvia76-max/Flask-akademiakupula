"""
Script para actualizar la base de datos con las tablas de lista de deseos y carrito.
Ejecuta este script después de añadir los modelos a tu archivo models.py.

IMPORTANTE: Este script debe ejecutarse desde el entorno virtual de Python.
Activa el entorno virtual antes de ejecutar este script:

En Windows:
venv\Scripts\activate

En macOS/Linux:
source venv/bin/activate
"""

import os
import sys

# Instrucciones para el usuario
print("Asegúrate de haber activado el entorno virtual antes de ejecutar este script.")
print("Asegúrate también de haber añadido los modelos Wishlist y Cart a tu archivo models.py.")
print()

# Intenta importar los módulos necesarios
try:
    # Importa los módulos según la estructura de tu proyecto
    # Estas importaciones pueden necesitar ajustes según tu estructura específica
    from run import app
    from models import db, Wishlist, Cart

    print("Importaciones exitosas.")
except ImportError as e:
    print(f"Error de importación: {e}")
    print("\nPosibles soluciones:")
    print("1. Asegúrate de haber activado el entorno virtual")
    print("2. Verifica la estructura de tu proyecto y ajusta las importaciones")
    print("3. Asegúrate de que los modelos Wishlist y Cart estén definidos en tu archivo models.py")
    sys.exit(1)

def update_database():
    """Actualiza la base de datos con las nuevas tablas."""
    try:
        with app.app_context():
            # Crea las tablas si no existen
            db.create_all()

            print("\nBase de datos actualizada con éxito.")
            print("Se han creado las siguientes tablas:")
            print("- wishlist")
            print("- cart")
    except Exception as e:
        print(f"\nError al actualizar la base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_database()
