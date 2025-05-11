import sqlite3
import datetime

def insert_contacto_direct(db_path, nombre, email, telefono, curso, mensaje):
    """Insert a contact directly into the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current schema to verify columns
        cursor.execute("PRAGMA table_info(contactos);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Available columns: {column_names}")
        
        # Insert the contact
        sql = """
        INSERT INTO contactos (nombre, email, telefono, curso, mensaje, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.datetime.now().isoformat()
        params = (nombre, email, telefono, curso, mensaje, now)
        
        cursor.execute(sql, params)
        conn.commit()
        
        # Verify the insertion
        last_id = cursor.lastrowid
        print(f"Contact inserted with ID: {last_id}")
        
        # Retrieve the inserted contact
        cursor.execute("SELECT * FROM contactos WHERE id = ?", (last_id,))
        contact = cursor.fetchone()
        
        if contact:
            print("Contact details:")
            for i, col in enumerate(column_names):
                print(f"  {col}: {contact[i]}")
            return True
        else:
            print("Failed to retrieve the inserted contact")
            return False
    except Exception as e:
        print(f"Error inserting contact: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_path = r"c:\users\betty\flask-akademiaKupula\instance\akademiakupula.db"
    
    # Insert a test contact
    insert_contacto_direct(
        db_path,
        "Test User Direct",
        "testdirect@example.com",
        "123456789",
        "maquillaje",
        "This is a test message inserted directly into the database."
    )
