"""
Script para verificar las tablas existentes en la base de datos.
"""

import os
import sys
import sqlite3
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
        logger.info("Verificando tablas en la base de datos")
        
        # Buscar archivos de base de datos en el directorio instance
        instance_dir = 'instance'
        if not os.path.exists(instance_dir):
            logger.error(f"El directorio {instance_dir} no existe")
            return False
        
        db_files = [f for f in os.listdir(instance_dir) if f.endswith('.db')]
        
        if not db_files:
            logger.error("No se encontraron archivos de base de datos en el directorio instance")
            return False
        
        logger.info(f"Archivos de base de datos encontrados: {db_files}")
        
        # Verificar cada archivo de base de datos
        for db_file in db_files:
            db_path = os.path.join(instance_dir, db_file)
            logger.info(f"Verificando tablas en {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obtener lista de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            logger.info(f"Tablas en {db_file}: {[table[0] for table in tables]}")
            
            # Verificar estructura de cada tabla
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                logger.info(f"Columnas en {table_name}: {[column[1] for column in columns]}")
            
            conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Error al verificar tablas: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        print("Verificación de tablas completada")
    else:
        print("Error al verificar tablas")
        sys.exit(1)
