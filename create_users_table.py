"""
Script para crear la tabla de usuarios en la base de datos.
Este script crea la tabla de usuarios si no existe.
"""

import os
import sqlite3
from app import create_app, db
from app.models.user import User

def create_users_table():
    """
    Crea la tabla de usuarios en la base de datos si no existe.
    """
    app = create_app()

    # Ruta a la base de datos
    db_path = os.path.join(app.root_path, '..', 'instance', 'akademiakupula.db')

    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"La base de datos no existe: {db_path}")
        print("Creando nueva base de datos...")

        # Crear la base de datos y las tablas
        with app.app_context():
            db.create_all()
            print("Base de datos creada exitosamente.")
            return

    # Conectar a la base de datos existente
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar si la tabla users existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("La tabla users no existe. Creando tabla...")
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
        conn.commit()
        print("Tabla users creada exitosamente.")
    else:
        print("La tabla users ya existe.")

    conn.close()

    # Crear un usuario de ejemplo directamente con SQL
    print("Creando usuario de ejemplo...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar si ya existe un usuario con el email de ejemplo
    cursor.execute("SELECT id FROM users WHERE email = ?", ("usuario@ejemplo.com",))
    if not cursor.fetchone():
        # Generar un hash de contraseña manualmente
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash("password123")

        # Insertar el usuario
        cursor.execute("""
        INSERT INTO users (full_name, postal_code, email, password_hash, is_confirmed)
        VALUES (?, ?, ?, ?, ?)
        """, ("Usuario de Prueba", "28001", "usuario@ejemplo.com", password_hash, 1))
        conn.commit()
        print("Usuario de ejemplo creado exitosamente.")
    else:
        print("El usuario de ejemplo ya existe.")

    conn.close()

if __name__ == "__main__":
    create_users_table()
    print("Proceso completado. La tabla de usuarios ha sido creada con éxito.")
