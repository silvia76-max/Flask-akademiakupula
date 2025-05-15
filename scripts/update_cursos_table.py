"""
Script para actualizar la tabla cursos y añadir las columnas faltantes.
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
        logging.FileHandler('scripts/update_cursos_table.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando actualización de la tabla cursos")
        
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
        
        # Verificar si la tabla cursos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cursos'")
        if not cursor.fetchone():
            logger.error("La tabla 'cursos' no existe")
            return
        
        # Verificar las columnas existentes
        cursor.execute("PRAGMA table_info(cursos)")
        columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Columnas existentes: {columns}")
        
        # Añadir columnas faltantes
        columns_to_add = {
            'imagen_url': 'TEXT',
            'nivel': 'TEXT',
            'instructor': 'TEXT',
            'destacado': 'BOOLEAN DEFAULT 0',
            'activo': 'BOOLEAN DEFAULT 1',
            'created_at': 'DATETIME',
            'updated_at': 'DATETIME'
        }
        
        for column, definition in columns_to_add.items():
            if column not in columns:
                try:
                    logger.info(f"Añadiendo columna: {column}")
                    cursor.execute(f"ALTER TABLE cursos ADD COLUMN {column} {definition}")
                    logger.info(f"Columna {column} añadida correctamente")
                except Exception as e:
                    logger.error(f"Error al añadir columna {column}: {str(e)}")
        
        # Guardar cambios
        conn.commit()
        logger.info("Cambios guardados correctamente")
        
        # Verificar las columnas actualizadas
        cursor.execute("PRAGMA table_info(cursos)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Columnas actualizadas: {updated_columns}")
        
        # Cerrar conexión
        conn.close()
        logger.info("Actualización de la tabla cursos completada")
        
        # Ahora vamos a probar la aplicación con la base de datos actualizada
        logger.info("Probando la aplicación con la base de datos actualizada")
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.models.curso import Curso
            
            # Intentar consultar cursos
            cursos = Curso.query.all()
            logger.info(f"Consulta exitosa. Cursos encontrados: {len(cursos)}")
            
            logger.info("Prueba completada con éxito")
        
    except Exception as e:
        logger.error(f"Error durante la actualización: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
