"""
Script para verificar las sesiones en la base de datos.
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
        logger.info("Verificando sesiones en la base de datos")
        
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
            logger.info(f"Verificando sesiones en {db_path}")
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
            cursor = conn.cursor()
            
            # Verificar si la tabla sessions existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            if not cursor.fetchone():
                logger.error(f"La tabla 'sessions' no existe en {db_file}")
                continue
            
            # Obtener todas las sesiones
            cursor.execute("SELECT * FROM sessions")
            sessions = cursor.fetchall()
            
            logger.info(f"Sesiones encontradas en {db_file}: {len(sessions)}")
            
            # Mostrar detalles de cada sesión
            for session in sessions:
                session_dict = {key: session[key] for key in session.keys()}
                logger.info(f"Sesión: {session_dict}")
            
            # Verificar usuarios
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            logger.info(f"Usuarios encontrados en {db_file}: {len(users)}")
            
            # Mostrar detalles de cada usuario
            for user in users:
                user_dict = {key: user[key] for key in user.keys()}
                logger.info(f"Usuario: {user_dict}")
            
            conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Error al verificar sesiones: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        print("Verificación de sesiones completada")
    else:
        print("Error al verificar sesiones")
        sys.exit(1)
