from flask_sqlalchemy import SQLAlchemy

# Inicializa SQLAlchemy
db = SQLAlchemy()

# Importa los modelos
from .user import User
from .curso import Curso
from .contacto import Contacto
