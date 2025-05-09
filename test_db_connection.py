"""
Script para probar la conexión a la base de datos y la inicialización de SQLAlchemy.
"""

from app import create_app, db
from app.models.user import User
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_db_connection():
    """
    Prueba la conexión a la base de datos y la inicialización de SQLAlchemy.
    """
    try:
        logger.info("Creando aplicación Flask")
        app = create_app()
        
        logger.info("Entrando en el contexto de la aplicación")
        with app.app_context():
            logger.info("Verificando la conexión a la base de datos")
            
            # Verificar si podemos acceder a la tabla de usuarios
            users_count = User.query.count()
            logger.info(f"Número de usuarios en la base de datos: {users_count}")
            
            # Listar todos los usuarios
            users = User.query.all()
            logger.info(f"Usuarios en la base de datos ({len(users)}):")
            for user in users:
                logger.info(f"  ID: {user.id}, Email: {user.email}, Nombre: {user.full_name}")
            
            logger.info("Conexión a la base de datos exitosa")
            
            # Intentar crear un usuario de prueba
            logger.info("Intentando crear un usuario de prueba")
            try:
                # Verificar si el usuario ya existe
                test_user = User.query.filter_by(email="test_db@example.com").first()
                
                if test_user:
                    logger.info(f"Usuario de prueba ya existe: ID {test_user.id}")
                else:
                    # Crear un nuevo usuario
                    new_user = User(
                        full_name="Test DB User",
                        postal_code="12345",
                        email="test_db@example.com",
                        is_confirmed=True
                    )
                    new_user.set_password("password123")
                    
                    # Guardar en la base de datos
                    db.session.add(new_user)
                    db.session.commit()
                    logger.info(f"Usuario de prueba creado con ID: {new_user.id}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error al crear usuario de prueba: {e}")
        
        logger.info("Prueba de conexión a la base de datos completada")
        return True
    except Exception as e:
        logger.error(f"Error en la prueba de conexión a la base de datos: {e}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    if success:
        print("✅ La conexión a la base de datos y la inicialización de SQLAlchemy funcionan correctamente")
    else:
        print("❌ Hubo un problema con la conexión a la base de datos o la inicialización de SQLAlchemy")
