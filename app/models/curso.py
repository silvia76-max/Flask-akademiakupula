from app import db

class Curso(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    duracion = db.Column(db.String(50), nullable=True)
    precio = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Curso {self.titulo}>'