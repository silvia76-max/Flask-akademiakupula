"""
Script para limpiar la base de datos eliminando tablas redundantes o innecesarias.
"""

import os
import sys
import sqlite3
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scripts/clean_db.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        db_path = 'instance/akademiaKupula.db'

        if not os.path.exists(db_path):
            logger.error(f"El archivo de base de datos {db_path} no existe")
            return False

        logger.info(f"Conectando a la base de datos: {db_path}")

        # Crear una copia de seguridad antes de hacer cambios
        backup_path = f"{db_path}.bak"
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        logger.info(f"Copia de seguridad creada en: {backup_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Lista de tablas a eliminar
        tables_to_drop = [
            'test_users',  # Tabla de prueba que no parece estar en uso
            'content'  # Tabla de contenido que no está en uso
        ]

        # Eliminar tablas
        for table in tables_to_drop:
            try:
                logger.info(f"Eliminando tabla: {table}")
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                logger.info(f"Tabla {table} eliminada correctamente")
            except Exception as e:
                logger.error(f"Error al eliminar tabla {table}: {str(e)}")

        # Vaciar la tabla sqlite_sequence para reiniciar los contadores de autoincremento
        try:
            logger.info("Vaciando tabla sqlite_sequence para reiniciar contadores de autoincremento")
            cursor.execute("DELETE FROM sqlite_sequence")
            logger.info("Tabla sqlite_sequence vaciada correctamente")
        except Exception as e:
            logger.error(f"Error al vaciar tabla sqlite_sequence: {str(e)}")

        # Limpiar sesiones inactivas o antiguas
        try:
            logger.info("Limpiando sesiones inactivas o antiguas")
            cursor.execute("DELETE FROM sessions WHERE is_active = 0 OR ended_at IS NOT NULL")
            deleted_sessions = cursor.rowcount
            logger.info(f"Se eliminaron {deleted_sessions} sesiones inactivas o antiguas")
        except Exception as e:
            logger.error(f"Error al limpiar sesiones: {str(e)}")

        # Guardar cambios
        conn.commit()
        conn.close()

        logger.info("Limpieza de la base de datos completada")
        return True
    except Exception as e:
        logger.error(f"Error durante la limpieza de la base de datos: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        print("\nLimpieza de la base de datos completada correctamente")
    else:
        print("\nError durante la limpieza de la base de datos")
        sys.exit(1)
