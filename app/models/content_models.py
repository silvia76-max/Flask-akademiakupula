from datetime import datetime, timezone
from app import db

class ContentType:
    """Enumeración de tipos de contenido."""
    VIDEO = 'video'
    IMAGE = 'image'
    STORY = 'story'
    TESTIMONIAL = 'testimonial'
    BANNER = 'banner'
    HERO = 'hero'

class ContentSection:
    """Enumeración de secciones donde se puede mostrar el contenido."""
    HOME = 'home'
    ABOUT = 'about'
    COURSES = 'courses'
    CONTACT = 'contact'
    TESTIMONIALS = 'testimonials'
    PROFILE = 'profile'
    COURSE_DETAIL = 'course_detail'

class Content(db.Model):
    """Modelo para almacenar contenido multimedia (videos, imágenes, historias)."""
    
    __tablename__ = 'contents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content_type = db.Column(db.String(20), nullable=False)  # video, image, story, testimonial, banner, hero
    section = db.Column(db.String(30), nullable=False)  # home, about, courses, contact, testimonials, profile
    url = db.Column(db.String(255), nullable=True)  # URL del recurso (video, imagen)
    content_text = db.Column(db.Text, nullable=True)  # Texto para historias o testimonios
    order = db.Column(db.Integer, default=0)  # Orden de aparición en la sección
    is_active = db.Column(db.Boolean, default=True)  # Si el contenido está activo
    
    # Metadatos adicionales (para videos)
    duration = db.Column(db.Integer, nullable=True)  # Duración en segundos
    thumbnail_url = db.Column(db.String(255), nullable=True)  # URL de la miniatura
    
    # Metadatos para testimonios
    author_name = db.Column(db.String(100), nullable=True)  # Nombre del autor del testimonio
    author_title = db.Column(db.String(100), nullable=True)  # Título o profesión del autor
    author_image_url = db.Column(db.String(255), nullable=True)  # Imagen del autor
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        """Representación en string del contenido."""
        return f'<Content {self.id}: {self.title} ({self.content_type})>'
    
    def to_dict(self):
        """Convierte el contenido a un diccionario para la API."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'section': self.section,
            'url': self.url,
            'content_text': self.content_text,
            'order': self.order,
            'is_active': self.is_active,
            'duration': self.duration,
            'thumbnail_url': self.thumbnail_url,
            'author_name': self.author_name,
            'author_title': self.author_title,
            'author_image_url': self.author_image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_section(cls, section, active_only=True):
        """Obtiene el contenido de una sección específica."""
        query = cls.query.filter_by(section=section)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.order).all()
    
    @classmethod
    def get_by_type(cls, content_type, active_only=True):
        """Obtiene el contenido de un tipo específico."""
        query = cls.query.filter_by(content_type=content_type)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.order).all()
    
    @classmethod
    def get_by_section_and_type(cls, section, content_type, active_only=True):
        """Obtiene el contenido de una sección y tipo específicos."""
        query = cls.query.filter_by(section=section, content_type=content_type)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.order).all()
