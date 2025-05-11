# Este archivo permite importar los modelos desde app.models
# Importa los modelos después de que se haya inicializado la aplicación
# para evitar importaciones circulares

# Estos imports se harán cuando se importe este módulo
# pero después de que la aplicación esté inicializada
def register_models():
    from .user import User
    from .curso import Curso
    from .contacto import Contacto
    from .wishlist import Wishlist
    from .cart import Cart

    return {
        'User': User,
        'Curso': Curso,
        'Contacto': Contacto,
        'Wishlist': Wishlist,
        'Cart': Cart
    }
