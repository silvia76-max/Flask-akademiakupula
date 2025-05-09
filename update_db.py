from app import create_app, db
from app.models.contacto import Contacto
from app.models.user import User
from app.models.curso import Curso
import sqlite3
import os

app = create_app()

def update_contacto_table():
    """
    Actualiza la tabla de contactos para agregar los campos telefono y curso
    """
    with app.app_context():
        # Verificar si la tabla ya tiene las columnas
        conn = sqlite3.connect('instance/akademiakupula.db')
        cursor = conn.cursor()
        
        # Verificar si la columna telefono existe
        cursor.execute("PRAGMA table_info(contactos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'telefono' not in columns:
            print("Agregando columna 'telefono' a la tabla contactos...")
            cursor.execute("ALTER TABLE contactos ADD COLUMN telefono TEXT")
        else:
            print("La columna 'telefono' ya existe en la tabla contactos")
            
        if 'curso' not in columns:
            print("Agregando columna 'curso' a la tabla contactos...")
            cursor.execute("ALTER TABLE contactos ADD COLUMN curso TEXT")
        else:
            print("La columna 'curso' ya existe en la tabla contactos")
            
        conn.commit()
        conn.close()
        
        print("Actualización de la base de datos completada")

if __name__ == '__main__':
    update_contacto_table()
