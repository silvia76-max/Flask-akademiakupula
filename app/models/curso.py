from datetime import datetime, timezone
from app import db, cache

class Curso(db.Model):
    """Modelo para los cursos ofrecidos en la plataforma."""

    __tablename__ = 'cursos'

    # Campos básicos
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=False)
    duracion = db.Column(db.String(50), nullable=True)
    precio = db.Column(db.Float, nullable=True)

    # Campos adicionales
    imagen_url = db.Column(db.String(255), nullable=True)
    nivel = db.Column(db.String(50), nullable=True)  # Principiante, Intermedio, Avanzado
    instructor = db.Column(db.String(100), nullable=True)
    destacado = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)

    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """Representación en string del curso."""
        return f'<Curso {self.id}: {self.titulo}>'

    def to_dict(self):
        """Convierte el curso a un diccionario para la API."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'duracion': self.duracion,
            'precio': float(self.precio) if self.precio else None,
            'imagen_url': self.imagen_url,
            'nivel': self.nivel,
            'instructor': self.instructor,
            'destacado': self.destacado,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    @cache.memoize(timeout=300)  # Caché de 5 minutos
    def get_all_active(cls):
        """Obtiene todos los cursos activos (con caché)."""
        return cls.query.filter_by(activo=True).order_by(cls.titulo).all()

    @classmethod
    @cache.memoize(timeout=300)  # Caché de 5 minutos
    def get_featured(cls):
        """Obtiene los cursos destacados (con caché)."""
        return cls.query.filter_by(activo=True, destacado=True).order_by(cls.titulo).all()

    @classmethod
    @cache.memoize(timeout=60)  # Caché de 1 minuto
    def get_by_id(cls, curso_id):
        """Obtiene un curso por su ID (con caché)."""
        return cls.query.get(curso_id)