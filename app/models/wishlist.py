"""
Modelo para la lista de deseos (wishlist) de los usuarios.
"""

from datetime import datetime, timezone
from app import db

class Wishlist(db.Model):
    """Modelo para la lista de deseos de los usuarios."""
    
    __tablename__ = 'wishlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    user = db.relationship('User', backref=db.backref('wishlist_items', lazy=True))
    curso = db.relationship('Curso', backref=db.backref('wishlist_items', lazy=True))
    
    def __init__(self, user_id, curso_id):
        self.user_id = user_id
        self.curso_id = curso_id
    
    def __repr__(self):
        return f'<Wishlist {self.id}: User {self.user_id}, Curso {self.curso_id}>'
    
    def to_dict(self):
        """Convierte el item de wishlist a un diccionario para la API."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'curso_id': self.curso_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
