"""
Script para crear todas las tablas en la base de datos.
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando creación de todas las tablas")
        
        # Añadir el directorio del proyecto al path
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, project_dir)
        
        # Importar las dependencias necesarias
        from app import create_app, db
        
        # Importar todos los modelos para asegurarnos de que se registren
        from app.models.user import User
        from app.models.curso import Curso
        from app.models.session import Session
        from app.models.order import Order, OrderItem
        
        app = create_app()
        
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            logger.info("Todas las tablas creadas correctamente")
            
            # Verificar que las tablas se han creado correctamente
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            logger.info(f"Tablas en la base de datos: {tables}")
            
            # Verificar que las tablas principales existen
            required_tables = ['users', 'cursos', 'sessions', 'orders', 'order_items']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Faltan las siguientes tablas: {missing_tables}")
                return False
            
            logger.info("Todas las tablas requeridas existen")
        
        logger.info("Proceso completado")
        
        return True
    except Exception as e:
        logger.error(f"Error durante la creación de tablas: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        print("Todas las tablas creadas correctamente")
    else:
        print("Error al crear las tablas")
        sys.exit(1)
