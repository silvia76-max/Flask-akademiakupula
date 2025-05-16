"""
Script para crear la tabla de sesiones en la base de datos.
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
        logging.FileHandler('scripts/create_sessions_table.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando creación de la tabla de sesiones")
        
        # Añadir el directorio del proyecto al path
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, project_dir)
        
        # Importar las dependencias necesarias
        from app import create_app, db
        from app.models.session import Session
        
        app = create_app()
        
        with app.app_context():
            # Verificar si la tabla ya existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            if 'sessions' in inspector.get_table_names():
                logger.info("La tabla 'sessions' ya existe en la base de datos")
            else:
                # Crear la tabla
                db.create_all()
                logger.info("Tabla 'sessions' creada correctamente")
            
            # Verificar que la tabla se ha creado correctamente
            if 'sessions' in inspector.get_table_names():
                logger.info("Verificación exitosa: La tabla 'sessions' existe en la base de datos")
            else:
                logger.error("Error: La tabla 'sessions' no se ha creado correctamente")
        
        logger.info("Proceso completado")
        
    except Exception as e:
        logger.error(f"Error durante la creación de la tabla: {str(e)}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    if main():
        print("Tabla de sesiones creada correctamente")
    else:
        print("Error al crear la tabla de sesiones")
        sys.exit(1)
