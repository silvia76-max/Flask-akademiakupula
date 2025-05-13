from datetime import datetime, timezone
from app import db, cache

class Content(db.Model):
    """Modelo para el contenido del sitio web."""
    
    __tablename__ = 'content'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    image_url = db.Column(db.String(255))
    published = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    content_type = db.Column(db.String(50), default='page')  # page, blog, news, etc.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', backref=db.backref('content_items', lazy=True))
    
    def __repr__(self):
        """Representación en string del contenido."""
        return f'<Content {self.id}: {self.title}>'
    
    def to_dict(self):
        """Convierte el contenido a un diccionario para la API."""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'summary': self.summary,
            'image_url': self.image_url,
            'published': self.published,
            'featured': self.featured,
            'content_type': self.content_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author.to_dict() if self.author else None
        }
    
    @classmethod
    @cache.memoize(timeout=300)  # Caché de 5 minutos
    def get_by_slug(cls, slug):
        """Obtiene un contenido por su slug (con caché)."""
        return cls.query.filter_by(slug=slug, published=True).first()
    
    @classmethod
    @cache.memoize(timeout=300)  # Caché de 5 minutos
    def get_featured(cls, content_type=None):
        """Obtiene los contenidos destacados (con caché)."""
        query = cls.query.filter_by(published=True, featured=True)
        if content_type:
            query = query.filter_by(content_type=content_type)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    @cache.memoize(timeout=300)  # Caché de 5 minutos
    def get_latest(cls, content_type=None, limit=5):
        """Obtiene los contenidos más recientes (con caché)."""
        query = cls.query.filter_by(published=True)
        if content_type:
            query = query.filter_by(content_type=content_type)
        return query.order_by(cls.created_at.desc()).limit(limit).all()
