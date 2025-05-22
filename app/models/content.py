"""
Modelo para contenido (este archivo se ha creado para mantener la compatibilidad).

NOTA: Este modelo ya no se utiliza y la tabla correspondiente ha sido eliminada de la base de datos.
Se mantiene este archivo solo por compatibilidad con código existente.
"""

from datetime import datetime, timezone

# Clase ficticia para mantener compatibilidad
class Content:
    """
    Modelo para contenido (ficticio).

    Nota: Este modelo se mantiene por compatibilidad, pero la tabla correspondiente
    ha sido eliminada de la base de datos. No hereda de db.Model para evitar
    que SQLAlchemy intente crear la tabla.
    """

    def __init__(self, id=None, title=None, content=None):
        self.id = id
        self.title = title
        self.content = content
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f'<Content {self.id}: {self.title}>'

    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
