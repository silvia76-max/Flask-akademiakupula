from datetime import datetime, timezone
from app import db
from sqlalchemy import Index

class Contacto(db.Model):
    """Modelo para los mensajes de contacto recibidos a través del formulario."""

    __tablename__ = 'contactos'

    # Campos básicos
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    telefono = db.Column(db.String(20), nullable=True)
    curso = db.Column(db.String(50), nullable=True)
    mensaje = db.Column(db.Text, nullable=False)

    # Estado del contacto
    estado = db.Column(db.String(20), default='nuevo')  # nuevo, en_proceso, respondido, cerrado

    # Campos de auditoría
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = db.Column(db.DateTime, nullable=True)

    # Índices adicionales
    __table_args__ = (
        Index('idx_contactos_estado_fecha', 'estado', 'fecha_creacion'),
    )

    def __repr__(self):
        """Representación en string del contacto."""
        return f'<Contacto {self.id}: {self.email}>'

    def to_dict(self):
        """Convierte el contacto a un diccionario para la API."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'curso': self.curso,
            'mensaje': self.mensaje,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    @classmethod
    def get_by_estado(cls, estado):
        """Obtiene los contactos por estado."""
        return cls.query.filter_by(estado=estado).order_by(cls.fecha_creacion.desc()).all()

    @classmethod
    def get_recientes(cls, limit=10):
        """Obtiene los contactos más recientes."""
        return cls.query.order_by(cls.fecha_creacion.desc()).limit(limit).all()
