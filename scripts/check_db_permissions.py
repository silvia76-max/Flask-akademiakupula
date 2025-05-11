import sqlite3
import os

def check_db_permissions(db_path):
    """Check if we have write permissions to the database."""
    try:
        # Check if file exists
        if not os.path.exists(db_path):
            print(f"Database file does not exist: {db_path}")
            return False
        
        # Check if we can read the file
        if not os.access(db_path, os.R_OK):
            print(f"Cannot read database file: {db_path}")
            return False
        
        # Check if we can write to the file
        if not os.access(db_path, os.W_OK):
            print(f"Cannot write to database file: {db_path}")
            return False
        
        # Try to connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Try to create a temporary table
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS temp_test (id INTEGER PRIMARY KEY)")
            conn.commit()
            print("Successfully created temporary table")
            
            # Try to insert data
            cursor.execute("INSERT INTO temp_test (id) VALUES (1)")
            conn.commit()
            print("Successfully inserted data into temporary table")
            
            # Try to delete data
            cursor.execute("DELETE FROM temp_test WHERE id = 1")
            conn.commit()
            print("Successfully deleted data from temporary table")
            
            # Try to drop the table
            cursor.execute("DROP TABLE temp_test")
            conn.commit()
            print("Successfully dropped temporary table")
            
            print("All database operations successful!")
            return True
        except Exception as e:
            print(f"Error performing database operations: {e}")
            return False
        finally:
            conn.close()
    except Exception as e:
        print(f"Error checking database permissions: {e}")
        return False

if __name__ == "__main__":
    db_path = r"c:\users\betty\flask-akademiaKupula\instance\akademiakupula.db"
    check_db_permissions(db_path)
