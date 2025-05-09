"""
Script para actualizar la estructura de la tabla de contactos.
Este script modifica la tabla de contactos para agregar los campos telefono y curso.
"""

import os
import sqlite3
from app import create_app, db

def update_contacto_table():
    """
    Actualiza la tabla de contactos para agregar los campos telefono y curso.
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

    # Verificar si la tabla contactos existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contactos'")
    if not cursor.fetchone():
        print("La tabla contactos no existe. Creando tabla...")
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
        conn.commit()
        print("Tabla contactos creada exitosamente.")
        conn.close()
        return

    # Verificar si las columnas telefono y curso existen
    cursor.execute("PRAGMA table_info(contactos)")
    columns = [column[1] for column in cursor.fetchall()]

    # Agregar columna telefono si no existe
    if 'telefono' not in columns:
        print("Agregando columna 'telefono' a la tabla contactos...")
        cursor.execute("ALTER TABLE contactos ADD COLUMN telefono VARCHAR(20)")
    else:
        print("La columna 'telefono' ya existe en la tabla contactos")

    # Agregar columna curso si no existe
    if 'curso' not in columns:
        print("Agregando columna 'curso' a la tabla contactos...")
        cursor.execute("ALTER TABLE contactos ADD COLUMN curso VARCHAR(50)")
    else:
        print("La columna 'curso' ya existe en la tabla contactos")

    conn.commit()
    conn.close()
    print("Actualización de la tabla contactos completada.")

if __name__ == "__main__":
    update_contacto_table()
    print("Proceso completado. La base de datos ha sido actualizada con éxito.")
