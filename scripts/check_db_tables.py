"""
Script para verificar las tablas en la base de datos y mostrar su estructura.
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
        logging.FileHandler('scripts/db_tables_report.log')
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

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        logger.info(f"Tablas encontradas: {len(tables)}")

        for table in tables:
            table_name = table['name']
            logger.info(f"\n{'=' * 50}")
            logger.info(f"TABLA: {table_name}")
            logger.info(f"{'=' * 50}")

            # Obtener estructura de la tabla
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            logger.info("Estructura de la tabla:")
            for col in columns:
                logger.info(f"  - {col['name']} ({col['type']}){' PRIMARY KEY' if col['pk'] else ''}{' NOT NULL' if col['notnull'] else ''}")

            # Contar registros en la tabla
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            logger.info(f"Número de registros: {count}")

            # Mostrar algunos registros de ejemplo si hay datos
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()

                logger.info("Ejemplos de registros:")
                for i, row in enumerate(rows):
                    logger.info(f"  Registro {i+1}:")
                    for key in row.keys():
                        logger.info(f"    {key}: {row[key]}")

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al verificar tablas: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        print("\nVerificación de tablas completada")
    else:
        print("\nError al verificar tablas")
        sys.exit(1)
