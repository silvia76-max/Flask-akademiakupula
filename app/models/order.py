from datetime import datetime, timezone
from app import db

class Order(db.Model):
    """Modelo para las órdenes de compra."""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, paid, cancelled, refunded
    payment_method = db.Column(db.String(50))
    payment_id = db.Column(db.String(255))  # ID de referencia del sistema de pago
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        """Representación en string de la orden."""
        return f'<Order {self.id}: {self.status}>'
    
    def to_dict(self):
        """Convierte la orden a un diccionario para la API."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_id': self.payment_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    """Modelo para los items de una orden de compra."""
    
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    
    # Relaciones
    curso = db.relationship('Curso', backref=db.backref('order_items', lazy=True))
    
    def __repr__(self):
        """Representación en string del item de orden."""
        return f'<OrderItem {self.id}: Order {self.order_id}, Curso {self.curso_id}>'
    
    def to_dict(self):
        """Convierte el item de orden a un diccionario para la API."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'curso_id': self.curso_id,
            'quantity': self.quantity,
            'price': float(self.price),
            'curso': self.curso.to_dict() if self.curso else None
        }
