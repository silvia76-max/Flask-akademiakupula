"""
Script para crear las tablas de wishlist y cart usando Flask y SQLAlchemy.
"""

import logging
import sys

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
        logger.info("Iniciando creación de tablas wishlist y cart")
        
        # Importar la aplicación Flask
        from app import create_app, db
        
        # Crear la aplicación
        app = create_app()
        
        # Importar los modelos
        from app.models.wishlist import Wishlist
        from app.models.cart import Cart
        
        # Crear las tablas
        with app.app_context():
            db.create_all()
            logger.info("Tablas creadas correctamente")
            
            # Verificar que las tablas se hayan creado
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            if 'wishlist' in inspector.get_table_names() and 'cart' in inspector.get_table_names():
                logger.info("Tablas wishlist y cart creadas correctamente")
            else:
                logger.warning(f"No se pudieron crear todas las tablas. Tablas encontradas: {inspector.get_table_names()}")
        
        logger.info("Proceso completado con éxito")
        
    except Exception as e:
        logger.error(f"Error durante la creación de tablas: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
