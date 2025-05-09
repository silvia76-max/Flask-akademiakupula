"""
Script para probar la inserción de datos en la base de datos.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

def test_insert():
    """
    Prueba la inserción de datos en la base de datos.
    """
    # Ruta a la base de datos
    db_path = os.path.join('instance', 'akademiakupula.db')
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insertar un usuario de prueba
    try:
        # Generar un hash de contraseña
        password_hash = generate_password_hash('password123')
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM users WHERE email = ?", ('test@example.com',))
        if cursor.fetchone():
            print("El usuario de prueba ya existe. Actualizando...")
            cursor.execute("""
            UPDATE users 
            SET full_name = ?, postal_code = ?, password_hash = ?, is_confirmed = ?
            WHERE email = ?
            """, ('Usuario de Prueba 2', '28002', password_hash, 1, 'test@example.com'))
        else:
            print("Insertando usuario de prueba...")
            cursor.execute("""
            INSERT INTO users (full_name, postal_code, email, password_hash, is_confirmed)
            VALUES (?, ?, ?, ?, ?)
            """, ('Usuario de Prueba 2', '28002', 'test@example.com', password_hash, 1))
        
        # Guardar cambios
        conn.commit()
        print("Usuario de prueba insertado/actualizado exitosamente.")
        
        # Verificar que el usuario se haya insertado correctamente
        cursor.execute("SELECT * FROM users WHERE email = ?", ('test@example.com',))
        user = cursor.fetchone()
        print(f"Usuario insertado: {user}")
    except Exception as e:
        conn.rollback()
        print(f"Error al insertar usuario de prueba: {e}")
    
    # Insertar un contacto de prueba
    try:
        # Verificar si el contacto ya existe
        cursor.execute("SELECT id FROM contactos WHERE email = ?", ('test@example.com',))
        if cursor.fetchone():
            print("El contacto de prueba ya existe. Actualizando...")
            cursor.execute("""
            UPDATE contactos 
            SET nombre = ?, telefono = ?, curso = ?, mensaje = ?
            WHERE email = ?
            """, ('Contacto de Prueba', '612345678', 'maquillaje', 'Mensaje de prueba actualizado', 'test@example.com'))
        else:
            print("Insertando contacto de prueba...")
            cursor.execute("""
            INSERT INTO contactos (nombre, email, telefono, curso, mensaje)
            VALUES (?, ?, ?, ?, ?)
            """, ('Contacto de Prueba', 'test@example.com', '612345678', 'maquillaje', 'Mensaje de prueba'))
        
        # Guardar cambios
        conn.commit()
        print("Contacto de prueba insertado/actualizado exitosamente.")
        
        # Verificar que el contacto se haya insertado correctamente
        cursor.execute("SELECT * FROM contactos WHERE email = ?", ('test@example.com',))
        contacto = cursor.fetchone()
        print(f"Contacto insertado: {contacto}")
    except Exception as e:
        conn.rollback()
        print(f"Error al insertar contacto de prueba: {e}")
    
    # Cerrar conexión
    conn.close()
    print("Prueba de inserción completada.")

if __name__ == "__main__":
    test_insert()
