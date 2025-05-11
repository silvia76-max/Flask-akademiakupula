# Instrucciones para actualizar la base de datos

Para implementar la lista de deseos y el carrito de compra, necesitas añadir dos nuevas tablas a tu base de datos. Hay varias formas de hacerlo, dependiendo de tu configuración. Elige la opción que mejor se adapte a tu caso.

## Opción A: Usar el script interactivo

He creado un script interactivo que intentará detectar automáticamente la estructura de tu proyecto y actualizar la base de datos:

1. Asegúrate de estar en el entorno virtual de Python
2. Ejecuta el script:
   ```
   python update_db_interactive.py
   ```
3. Sigue las instrucciones en pantalla

## Opción B: Usar SQL directo

Si prefieres actualizar la base de datos directamente con SQL:

1. Abre tu base de datos SQLite con una herramienta como SQLite Browser o desde la línea de comandos:
   ```
   sqlite3 ruta/a/tu/base_de_datos.db
   ```
2. Ejecuta el script SQL:
   ```
   .read create_tables.sql
   ```
   O copia y pega el contenido del archivo `create_tables.sql` directamente.

## Opción C: Añadir los modelos a tu archivo models.py y usar Flask

Añade los siguientes modelos a tu archivo `models.py`:

```python
class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    user = db.relationship('User', backref=db.backref('wishlist_items', lazy=True))
    course = db.relationship('Course', backref=db.backref('wishlist_items', lazy=True))

    def __init__(self, user_id, course_id):
        self.user_id = user_id
        self.course_id = course_id

    def __repr__(self):
        return f'<Wishlist {self.id}: User {self.user_id}, Course {self.course_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    course = db.relationship('Course', backref=db.backref('cart_items', lazy=True))

    def __init__(self, user_id, course_id):
        self.user_id = user_id
        self.course_id = course_id

    def __repr__(self):
        return f'<Cart {self.id}: User {self.user_id}, Course {self.course_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

Asegúrate de que la importación de `datetime` esté presente en tu archivo:

```python
from datetime import datetime
```

## 2. Actualizar la base de datos

Hay varias formas de actualizar la base de datos:

### Opción 1: Usar Flask-Migrate (recomendado)

Si estás usando Flask-Migrate para gestionar las migraciones de la base de datos:

1. Activa tu entorno virtual:
   ```
   # En Windows
   venv\Scripts\activate

   # En macOS/Linux
   source venv/bin/activate
   ```

2. Genera una nueva migración:
   ```
   flask db migrate -m "Añadir tablas de wishlist y cart"
   ```

3. Aplica la migración:
   ```
   flask db upgrade
   ```

### Opción 2: Usar db.create_all()

Si no estás usando Flask-Migrate, puedes crear las tablas directamente:

1. Abre una consola Python en tu entorno virtual:
   ```
   # En Windows
   venv\Scripts\activate
   python

   # En macOS/Linux
   source venv/bin/activate
   python
   ```

2. Ejecuta los siguientes comandos:
   ```python
   from run import app  # Ajusta según tu estructura
   from models import db  # Ajusta según tu estructura

   with app.app_context():
       db.create_all()
   ```

### Opción 3: Ejecutar un script personalizado

Crea un archivo `update_db.py` con el siguiente contenido (ajusta las importaciones según tu estructura):

```python
from run import app  # Ajusta según tu estructura
from models import db  # Ajusta según tu estructura

with app.app_context():
    db.create_all()
    print("Base de datos actualizada con éxito.")
```

Luego ejecuta:
```
python update_db.py
```

## 3. Verificar que las tablas se hayan creado

Puedes verificar que las tablas se hayan creado correctamente usando una herramienta como SQLite Browser (si estás usando SQLite) o ejecutando consultas SQL directamente.

## 4. Añadir las rutas de la API

Crea un nuevo archivo para las rutas de la API (por ejemplo, `api/user_courses.py`) con el contenido del archivo `user_courses_routes.py` que te proporcioné.

## 5. Registrar el blueprint

En tu archivo principal (por ejemplo, `__init__.py` o `run.py`), registra el blueprint:

```python
from api.user_courses import user_courses
app.register_blueprint(user_courses, url_prefix='/api')
```

## 6. Reiniciar el servidor Flask

Reinicia tu servidor Flask para que los cambios surtan efecto.
