# Backend de Akademia Kupula

Este es el backend para la aplicación web Akademia Kupula, desarrollado con Flask.

## Características

- API RESTful para la gestión de cursos, usuarios y contactos
- Autenticación con JWT (JSON Web Tokens)
- Base de datos SQLite (configurable para PostgreSQL en producción)
- Optimizado para rendimiento con caché y compresión
- Seguridad mejorada con rate limiting y protección contra ataques comunes

## Requisitos

- Python 3.9+
- Pip (gestor de paquetes de Python)
- Entorno virtual (recomendado)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/Flask-akademiaKupula.git
   cd Flask-akademiaKupula
   ```

2. Crear y activar un entorno virtual:
   ```bash
   # En Windows
   python -m venv venv
   venv\Scripts\activate

   # En macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   - Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=tu-clave-secreta
   JWT_SECRET_KEY=tu-clave-jwt-secreta
   SQLALCHEMY_DATABASE_URI=sqlite:///akademiakupula.db
   
   # Configuración de correo (opcional)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=tu-email@gmail.com
   MAIL_PASSWORD=tu-contraseña
   MAIL_DEFAULT_SENDER=tu-email@gmail.com
   ```

5. Inicializar la base de datos:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Ejecución

Para ejecutar el servidor en modo desarrollo:

```bash
flask run
```

O alternativamente:

```bash
python run.py
```

El servidor estará disponible en `http://localhost:5000`.

## Estructura del Proyecto

```
Flask-akademiaKupula/
├── app/                    # Paquete principal de la aplicación
│   ├── models/             # Modelos de datos
│   ├── routes/             # Rutas de la API
│   ├── __init__.py         # Inicialización de la aplicación
│   └── utils.py            # Utilidades
├── migrations/             # Migraciones de la base de datos
├── instance/               # Datos de la instancia (base de datos)
├── .env                    # Variables de entorno
├── config.py               # Configuración de la aplicación
├── requirements.txt        # Dependencias
├── run.py                  # Punto de entrada
└── README.md               # Este archivo
```

## API Endpoints

### Autenticación

- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/profile` - Perfil de usuario (requiere autenticación)
- `POST /api/auth/refresh` - Refrescar token de acceso
- `POST /api/auth/logout` - Cerrar sesión

### Cursos

- `GET /api/cursos` - Obtener todos los cursos
- `GET /api/cursos/<id>` - Obtener un curso específico
- `POST /api/cursos` - Crear un nuevo curso (requiere autenticación)
- `PUT /api/cursos/<id>` - Actualizar un curso (requiere autenticación)
- `DELETE /api/cursos/<id>` - Eliminar un curso (requiere autenticación)

### Contacto

- `POST /api/contacto` - Enviar un mensaje de contacto
- `GET /api/contacto` - Obtener todos los mensajes (requiere autenticación)

## Optimizaciones Implementadas

1. **Caché**: Se utiliza Flask-Caching para almacenar en caché resultados de consultas frecuentes.
2. **Compresión**: Se comprime el contenido de las respuestas para reducir el tamaño de transferencia.
3. **Rate Limiting**: Se limita la cantidad de solicitudes por IP para prevenir abusos.
4. **Seguridad**: Se implementan cabeceras de seguridad y protección contra ataques comunes.
5. **Rendimiento de Base de Datos**: Se utilizan índices y consultas optimizadas.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
