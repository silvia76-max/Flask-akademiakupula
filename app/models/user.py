from flask_login import UserMixin
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from app import db, bcrypt, cache

class User(db.Model, UserMixin):
    """Modelo de usuario para la aplicación."""

    __tablename__ = 'users'

    # Campos básicos
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False, index=True)
    postal_code = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)

    # Campos de estado y seguridad
    is_confirmed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones (se pueden añadir según sea necesario)
    # Por ejemplo: wishlist, cart, orders, etc.

    def __repr__(self):
        """Representación en string del usuario."""
        return f'<User {self.id}: {self.email}>'

    def set_password(self, password):
        """Establece la contraseña del usuario."""
        try:
            # Usar bcrypt para mayor seguridad
            with open('password_debug.log', 'a') as f:
                f.write(f"Estableciendo contraseña para usuario: {self.email}\n")

            hashed = bcrypt.generate_password_hash(password).decode('utf-8')

            with open('password_debug.log', 'a') as f:
                f.write("Contraseña hasheada correctamente\n")

            self.password_hash = hashed

            with open('password_debug.log', 'a') as f:
                f.write("Contraseña establecida correctamente\n")
        except Exception as e:
            with open('password_debug.log', 'a') as f:
                f.write(f"Error al establecer contraseña: {str(e)}\n")
                import traceback
                f.write(traceback.format_exc())
            raise

    def check_password(self, password):
        """Verifica la contraseña del usuario."""
        # Si la cuenta está bloqueada, no permitir el login
        if self.is_locked:
            return False

        # Verificar contraseña
        is_valid = bcrypt.check_password_hash(self.password_hash, password)

        # Actualizar intentos de login
        if is_valid:
            self.failed_login_attempts = 0
            self.last_login = datetime.now(timezone.utc)
        else:
            self.failed_login_attempts += 1
            # Bloquear cuenta después de 5 intentos fallidos
            if self.failed_login_attempts >= 5:
                self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)

        return is_valid

    @hybrid_property
    def is_locked(self):
        """Indica si la cuenta está bloqueada."""
        if self.locked_until and self.locked_until > datetime.now(timezone.utc):
            return True
        # Si el tiempo de bloqueo ya pasó, desbloquear la cuenta
        if self.locked_until:
            self.locked_until = None
            self.failed_login_attempts = 0
        return False

    def to_dict(self):
        """Convierte el usuario a un diccionario para la API."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'postal_code': self.postal_code,
            'is_confirmed': self.is_confirmed,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    @classmethod
    @cache.memoize(timeout=60)  # Caché de 1 minuto
    def get_by_email(cls, email):
        """Obtiene un usuario por su email (con caché)."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def create_user(cls, full_name, email, password, postal_code, is_admin=False, is_confirmed=False):
        """Crea un nuevo usuario."""
        try:
            with open('user_create_debug.log', 'a') as f:
                f.write(f"Creando usuario: {full_name}, {email}, {postal_code}\n")

            # No usamos db.session directamente, sino que lo obtenemos del contexto actual
            from flask import current_app

            with open('user_create_debug.log', 'a') as f:
                f.write("Obteniendo contexto de la aplicación\n")

            user = cls(
                full_name=full_name,
                email=email,
                postal_code=postal_code,
                is_admin=is_admin,
                is_confirmed=is_confirmed
            )

            with open('user_create_debug.log', 'a') as f:
                f.write("Usuario instanciado correctamente\n")

            user.set_password(password)

            with open('user_create_debug.log', 'a') as f:
                f.write("Contraseña establecida correctamente\n")

            # Usamos la sesión de la aplicación actual
            from app import db as current_db

            with open('user_create_debug.log', 'a') as f:
                f.write("Obtenida instancia de db\n")

            current_db.session.add(user)

            with open('user_create_debug.log', 'a') as f:
                f.write("Usuario añadido a la sesión\n")

            current_db.session.commit()

            with open('user_create_debug.log', 'a') as f:
                f.write(f"Commit realizado correctamente. ID de usuario: {user.id}\n")

            return user
        except Exception as e:
            with open('user_create_debug.log', 'a') as f:
                f.write(f"Error al crear usuario: {str(e)}\n")
                import traceback
                f.write(traceback.format_exc())
            raise
