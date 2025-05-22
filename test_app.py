"""
Script para probar si la aplicación se inicia correctamente.
"""

import traceback

try:
    from app import create_app
    app = create_app()
    print('La aplicación se ha creado correctamente')
except Exception as e:
    traceback.print_exc()
