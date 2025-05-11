# Modelos para la lista de deseos y el carrito
# Añade estas clases a tu archivo models.py existente

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


# También necesitarás asegurarte de que tienes un modelo Course
# Si no lo tienes, aquí hay un ejemplo básico:

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))
    duration = db.Column(db.String(50))
    level = db.Column(db.String(50))
    instructor = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, title, description, price, image_url=None, duration=None, level=None, instructor=None):
        self.title = title
        self.description = description
        self.price = price
        self.image_url = image_url
        self.duration = duration
        self.level = level
        self.instructor = instructor
    
    def __repr__(self):
        return f'<Course {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': float(self.price),
            'image_url': self.image_url,
            'duration': self.duration,
            'level': self.level,
            'instructor': self.instructor,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
