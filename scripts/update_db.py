"""
Script para actualizar la estructura de la base de datos.
"""

import os
import sys
import logging
import sqlite3

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scripts/update_db.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando actualización de la base de datos")

        # Añadir el directorio del proyecto al path
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, project_dir)

        # Conectar a la base de datos
        db_path = 'instance/app.db'

        if not os.path.exists(db_path):
            logger.error(f"La base de datos no existe en la ruta: {db_path}")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("Conexión a la base de datos establecida")

        # Verificar si la tabla users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logger.error("La tabla 'users' no existe")
            return

        # Verificar las columnas existentes
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Columnas existentes: {columns}")

        # Añadir columnas faltantes
        columns_to_add = {
            'is_active': 'BOOLEAN DEFAULT 1',
            'is_admin': 'BOOLEAN DEFAULT 0',
            'last_login': 'DATETIME',
            'failed_login_attempts': 'INTEGER DEFAULT 0',
            'locked_until': 'DATETIME',
            'created_at': 'DATETIME',
            'updated_at': 'DATETIME'
        }

        for column, definition in columns_to_add.items():
            if column not in columns:
                try:
                    logger.info(f"Añadiendo columna: {column}")
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
                    logger.info(f"Columna {column} añadida correctamente")
                except Exception as e:
                    logger.error(f"Error al añadir columna {column}: {str(e)}")

        # Guardar cambios
        conn.commit()
        logger.info("Cambios guardados correctamente")

        # Verificar las columnas actualizadas
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Columnas actualizadas: {updated_columns}")

        # Cerrar conexión
        conn.close()
        logger.info("Actualización de la base de datos completada")

        # Ahora vamos a probar la aplicación
        logger.info("Probando la aplicación con la base de datos actualizada")

        from app import create_app
        app = create_app()

        with app.app_context():
            from app.models.user import User

            # Intentar consultar usuarios
            users = User.query.all()
            logger.info(f"Consulta exitosa. Usuarios encontrados: {len(users)}")

            logger.info("Prueba completada con éxito")

    except Exception as e:
        logger.error(f"Error durante la actualización: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
