from datetime import datetime
from app import db

class Order(db.Model):
    """
    Modelo para almacenar información de pedidos.
    
    Attributes:
        id (int): ID único del pedido
        user_id (int): ID del usuario que realizó el pedido
        total_amount (float): Monto total del pedido
        payment_status (str): Estado del pago (pending, completed, failed, refunded)
        payment_id (str): ID del pago en el proveedor (Stripe)
        payment_method (str): Método de pago utilizado
        created_at (datetime): Fecha y hora de creación del pedido
        updated_at (datetime): Fecha y hora de actualización del pedido
    """
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='pending')
    payment_id = db.Column(db.String(100), nullable=True)
    payment_method = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'
    
    def to_dict(self):
        """
        Convierte el pedido a un diccionario para la API.
        
        Returns:
            dict: Diccionario con los datos del pedido
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'payment_id': self.payment_id,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    """
    Modelo para almacenar los elementos de un pedido.
    
    Attributes:
        id (int): ID único del elemento
        order_id (int): ID del pedido al que pertenece
        course_id (str): ID del curso comprado
        price (float): Precio del curso al momento de la compra
        quantity (int): Cantidad (generalmente 1 para cursos)
    """
    
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    course_id = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'
    
    def to_dict(self):
        """
        Convierte el elemento del pedido a un diccionario para la API.
        
        Returns:
            dict: Diccionario con los datos del elemento
        """
        return {
            'id': self.id,
            'order_id': self.order_id,
            'course_id': self.course_id,
            'price': self.price,
            'quantity': self.quantity
        }
