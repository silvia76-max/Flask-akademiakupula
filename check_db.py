"""
Script para verificar la base de datos y crear tablas si no existen.
"""

import os
import sqlite3

def check_database():
    """
    Verifica la base de datos y crea tablas si no existen.
    """
    # Ruta a la base de datos
    db_path = os.path.join('instance', 'akademiakupula.db')
    
    # Verificar si el directorio instance existe
    if not os.path.exists('instance'):
        os.makedirs('instance')
        print("Directorio 'instance' creado.")
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar qué tablas existen
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tablas existentes: {tables}")
    
    # Crear tabla users si no existe
    if ('users',) not in tables:
        print("Creando tabla 'users'...")
        cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(120) NOT NULL,
            postal_code VARCHAR(20) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(128) NOT NULL,
            is_confirmed BOOLEAN DEFAULT 0
        )
        """)
        print("Tabla 'users' creada exitosamente.")
    else:
        print("La tabla 'users' ya existe.")
        
        # Mostrar estructura de la tabla users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("Estructura de la tabla 'users':")
        for column in columns:
            print(f"  {column}")
        
        # Mostrar datos de la tabla users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"Datos en la tabla 'users' ({len(users)} registros):")
        for user in users:
            print(f"  {user}")
    
    # Crear tabla contactos si no existe
    if ('contactos',) not in tables:
        print("Creando tabla 'contactos'...")
        cursor.execute("""
        CREATE TABLE contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(80) NOT NULL,
            email VARCHAR(120) NOT NULL,
            telefono VARCHAR(20),
            curso VARCHAR(50),
            mensaje TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("Tabla 'contactos' creada exitosamente.")
    else:
        print("La tabla 'contactos' ya existe.")
        
        # Mostrar estructura de la tabla contactos
        cursor.execute("PRAGMA table_info(contactos)")
        columns = cursor.fetchall()
        print("Estructura de la tabla 'contactos':")
        for column in columns:
            print(f"  {column}")
        
        # Mostrar datos de la tabla contactos
        cursor.execute("SELECT * FROM contactos")
        contactos = cursor.fetchall()
        print(f"Datos en la tabla 'contactos' ({len(contactos)} registros):")
        for contacto in contactos:
            print(f"  {contacto}")
    
    # Guardar cambios y cerrar conexión
    conn.commit()
    conn.close()
    print("Verificación de la base de datos completada.")

if __name__ == "__main__":
    check_database()
