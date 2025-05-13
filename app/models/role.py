from app import db

class Role(db.Model):
    """Modelo para los roles de usuario en el sistema."""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relación con los usuarios
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        """Representación en string del rol."""
        return f'<Role {self.name}>'
    
    @staticmethod
    def insert_roles():
        """Inserta los roles predefinidos en la base de datos."""
        roles = {
            'user': 'Usuario estándar',
            'admin': 'Administrador con acceso completo'
        }
        
        for role_name, description in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name, description=description)
                db.session.add(role)
        
        db.session.commit()
