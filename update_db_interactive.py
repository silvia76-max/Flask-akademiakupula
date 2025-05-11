"""
Script interactivo para actualizar la base de datos.
Este script te guiará paso a paso para identificar la estructura de tu proyecto
y actualizar la base de datos correctamente.
"""

import os
import sys
import importlib.util

def print_header(text):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60 + "\n")

def print_step(number, text):
    """Imprime un paso numerado."""
    print(f"\n--- Paso {number}: {text} ---\n")

def input_with_default(prompt, default=None):
    """Solicita entrada al usuario con un valor predeterminado."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()

def try_import(module_name, as_name=None):
    """Intenta importar un módulo y devuelve True si tiene éxito."""
    try:
        if as_name:
            globals()[as_name] = __import__(module_name)
        else:
            __import__(module_name)
        return True
    except ImportError:
        return False

def main():
    print_header("ACTUALIZACIÓN DE BASE DE DATOS PARA LISTA DE DESEOS Y CARRITO")
    
    print("""
Este script te ayudará a actualizar tu base de datos para añadir las tablas
necesarias para la lista de deseos y el carrito de compra.

Antes de continuar, asegúrate de:
1. Haber activado tu entorno virtual de Python
2. Estar en el directorio raíz de tu proyecto Flask
3. Haber añadido los modelos Wishlist y Cart a tu archivo models.py
""")
    
    input("Presiona Enter para continuar...")
    
    # Paso 1: Identificar la estructura del proyecto
    print_step(1, "Identificar la estructura del proyecto")
    
    print("""
Necesitamos identificar cómo está estructurado tu proyecto Flask.
Vamos a intentar diferentes importaciones comunes para encontrar tu aplicación.
""")
    
    # Intentar diferentes patrones de importación comunes
    app_found = False
    db_found = False
    app_module = None
    db_module = None
    
    # Lista de patrones de importación comunes para Flask
    import_patterns = [
        ("run", "app"),
        ("app", "app"),
        ("app", "create_app"),
        ("app.__init__", "app"),
        ("app.__init__", "create_app"),
        ("application", "app"),
        ("server", "app"),
        ("main", "app")
    ]
    
    for module_name, attr_name in import_patterns:
        try:
            print(f"Intentando importar {attr_name} desde {module_name}...")
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                app_module = module
                app_name = attr_name
                app_found = True
                print(f"¡Éxito! Se encontró {attr_name} en {module_name}")
                break
        except ImportError:
            print(f"No se pudo importar {module_name}")
    
    if not app_found:
        print("\nNo se pudo encontrar automáticamente tu aplicación Flask.")
        print("Vamos a intentar con información que proporciones.")
        
        module_name = input_with_default("Nombre del módulo donde está tu aplicación Flask (ej. app, run)", "run")
        attr_name = input_with_default("Nombre de la variable de la aplicación Flask (ej. app, application)", "app")
        
        try:
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                app_module = module
                app_name = attr_name
                app_found = True
                print(f"¡Éxito! Se encontró {attr_name} en {module_name}")
            else:
                print(f"No se encontró {attr_name} en {module_name}")
        except ImportError:
            print(f"No se pudo importar {module_name}")
    
    if not app_found:
        print("\nNo se pudo encontrar tu aplicación Flask.")
        print("Vamos a intentar un enfoque alternativo.")
        
        # Paso 2: Enfoque alternativo - SQLite directo
        print_step(2, "Enfoque alternativo - SQLite directo")
        
        print("""
Ya que no podemos acceder a tu aplicación Flask directamente,
vamos a intentar actualizar la base de datos usando SQLite directamente.

Para esto, necesitamos saber la ubicación de tu archivo de base de datos SQLite.
""")
        
        db_path = input_with_default("Ruta completa al archivo de base de datos SQLite", "instance/app.db")
        
        if not os.path.exists(db_path):
            print(f"No se encontró el archivo de base de datos en {db_path}")
            print("Por favor, proporciona la ruta correcta.")
            db_path = input("Ruta completa al archivo de base de datos SQLite: ")
        
        if not os.path.exists(db_path):
            print(f"No se encontró el archivo de base de datos en {db_path}")
            print("No podemos continuar sin acceso a la base de datos.")
            print("""
Alternativas:
1. Ejecuta este comando en una consola Python dentro de tu entorno virtual:
   
   from tu_app import app, db
   with app.app_context():
       db.create_all()
   
   (Ajusta 'tu_app' según la estructura de tu proyecto)

2. Si usas Flask-Migrate, ejecuta estos comandos en la terminal:
   
   flask db migrate -m "Añadir tablas de wishlist y cart"
   flask db upgrade
""")
            return
        
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Crear tabla wishlist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
            ''')
            
            # Crear tabla cart
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
            ''')
            
            conn.commit()
            conn.close()
            
            print("\n¡Éxito! Se han creado las tablas wishlist y cart en la base de datos.")
            return
        except Exception as e:
            print(f"Error al actualizar la base de datos: {e}")
            print("""
No se pudo actualizar la base de datos directamente.
Por favor, sigue las instrucciones en el archivo instrucciones_db.md
para actualizar la base de datos manualmente.
""")
            return
    
    # Si llegamos aquí, encontramos la aplicación Flask
    print("\n¡Bien! Hemos encontrado tu aplicación Flask.")
    
    # Paso 3: Buscar el objeto db
    print_step(3, "Buscar el objeto SQLAlchemy")
    
    # Lista de patrones de importación comunes para SQLAlchemy
    db_patterns = [
        ("models", "db"),
        ("app.models", "db"),
        ("app", "db"),
        ("app.__init__", "db"),
        ("database", "db"),
        ("app.database", "db")
    ]
    
    for module_name, attr_name in db_patterns:
        try:
            print(f"Intentando importar {attr_name} desde {module_name}...")
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                db_module = module
                db_name = attr_name
                db_found = True
                print(f"¡Éxito! Se encontró {attr_name} en {module_name}")
                break
        except ImportError:
            print(f"No se pudo importar {module_name}")
    
    if not db_found:
        print("\nNo se pudo encontrar automáticamente el objeto SQLAlchemy.")
        print("Vamos a intentar con información que proporciones.")
        
        module_name = input_with_default("Nombre del módulo donde está tu objeto SQLAlchemy (ej. models, app.models)", "models")
        attr_name = input_with_default("Nombre de la variable del objeto SQLAlchemy (ej. db)", "db")
        
        try:
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                db_module = module
                db_name = attr_name
                db_found = True
                print(f"¡Éxito! Se encontró {attr_name} en {module_name}")
            else:
                print(f"No se encontró {attr_name} en {module_name}")
        except ImportError:
            print(f"No se pudo importar {module_name}")
    
    if not db_found:
        print("\nNo se pudo encontrar el objeto SQLAlchemy.")
        print("""
No podemos continuar sin acceso al objeto SQLAlchemy.
Por favor, sigue las instrucciones en el archivo instrucciones_db.md
para actualizar la base de datos manualmente.
""")
        return
    
    # Paso 4: Actualizar la base de datos
    print_step(4, "Actualizar la base de datos")
    
    app = getattr(app_module, app_name)
    db = getattr(db_module, db_name)
    
    # Si app es una función factory, necesitamos llamarla
    if callable(app) and not hasattr(app, 'route'):
        print("Detectado que app es una función factory. Intentando crear la aplicación...")
        try:
            app = app()
        except Exception as e:
            print(f"Error al crear la aplicación: {e}")
            print("Por favor, sigue las instrucciones en el archivo instrucciones_db.md")
            return
    
    try:
        with app.app_context():
            db.create_all()
            print("\n¡Éxito! Se han creado las tablas wishlist y cart en la base de datos.")
    except Exception as e:
        print(f"Error al actualizar la base de datos: {e}")
        print("""
No se pudo actualizar la base de datos usando Flask.
Por favor, sigue las instrucciones en el archivo instrucciones_db.md
para actualizar la base de datos manualmente.
""")

if __name__ == "__main__":
    main()
