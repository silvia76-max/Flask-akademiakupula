"""
Script para añadir contenido de ejemplo a la base de datos.
"""

import os
import sys
from datetime import datetime, timezone

def add_sample_content():
    """
    Añade contenido de ejemplo a la base de datos.
    
    Este script debe ejecutarse después de haber creado la tabla de contenido.
    """
    try:
        # Añadir el directorio del proyecto al path
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, project_dir)
        
        # Importar las dependencias necesarias
        from app import create_app
        from app import db
        from app.models.content import Content
        
        app = create_app()
        
        # Definir contenido de ejemplo
        sample_contents = [
            # Imágenes para la sección de inicio
            {
                'title': 'Banner Principal',
                'description': 'Imagen principal para la página de inicio',
                'content_type': 'banner',
                'section': 'home',
                'url': '/static/img/banner-home.jpg',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Imagen de Servicios',
                'description': 'Imagen para la sección de servicios en la página de inicio',
                'content_type': 'image',
                'section': 'home',
                'url': '/static/img/services.jpg',
                'order': 2,
                'is_active': True
            },
            
            # Testimonios
            {
                'title': 'Testimonio de María',
                'description': 'Testimonio de una estudiante satisfecha',
                'content_type': 'testimonial',
                'section': 'testimonials',
                'content_text': 'Los cursos de Akademia Kupula han transformado mi carrera. Ahora tengo mi propio negocio de maquillaje y no podría estar más feliz.',
                'author_name': 'María García',
                'author_title': 'Maquilladora Profesional',
                'author_image_url': '/static/img/testimonial-1.jpg',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Testimonio de Carlos',
                'description': 'Testimonio de un estudiante satisfecho',
                'content_type': 'testimonial',
                'section': 'testimonials',
                'content_text': 'Gracias a los cursos de uñas, he podido abrir mi propio salón. La calidad de la enseñanza es excepcional.',
                'author_name': 'Carlos Rodríguez',
                'author_title': 'Propietario de Salón de Belleza',
                'author_image_url': '/static/img/testimonial-2.jpg',
                'order': 2,
                'is_active': True
            },
            
            # Historia para la sección Sobre Nosotros
            {
                'title': 'Nuestra Historia',
                'description': 'Historia de Akademia Kupula',
                'content_type': 'story',
                'section': 'about',
                'content_text': 'Akademia Kupula nació en 2015 con la misión de proporcionar educación de calidad en el campo de la belleza y la estética. Desde entonces, hemos formado a más de 1000 profesionales que ahora trabajan en todo el mundo.',
                'order': 1,
                'is_active': True
            },
            
            # Video para la sección de cursos
            {
                'title': 'Introducción al Maquillaje',
                'description': 'Video de introducción al curso de maquillaje',
                'content_type': 'video',
                'section': 'courses',
                'url': '/static/videos/intro-makeup.mp4',
                'thumbnail_url': '/static/img/thumbnail-makeup.jpg',
                'duration': 120,
                'order': 1,
                'is_active': True
            }
        ]
        
        # Añadir contenido a la base de datos
        with app.app_context():
            # Verificar si ya existe contenido
            existing_count = Content.query.count()
            if existing_count > 0:
                print(f"Ya existen {existing_count} elementos de contenido en la base de datos.")
                return True
            
            # Añadir contenido de ejemplo
            for content_data in sample_contents:
                content = Content(
                    title=content_data['title'],
                    description=content_data['description'],
                    content_type=content_data['content_type'],
                    section=content_data['section'],
                    url=content_data.get('url'),
                    content_text=content_data.get('content_text'),
                    order=content_data['order'],
                    is_active=content_data['is_active'],
                    duration=content_data.get('duration'),
                    thumbnail_url=content_data.get('thumbnail_url'),
                    author_name=content_data.get('author_name'),
                    author_title=content_data.get('author_title'),
                    author_image_url=content_data.get('author_image_url'),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.session.add(content)
            
            db.session.commit()
            print(f"Se han añadido {len(sample_contents)} elementos de contenido de ejemplo.")
        
        return True
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Asegúrate de que los archivos de modelos se han copiado correctamente.")
        return False
    except Exception as e:
        print(f"Error al añadir contenido de ejemplo: {e}")
        return False

if __name__ == "__main__":
    print("Añadiendo contenido de ejemplo...")
    if add_sample_content():
        print("\nContenido añadido con éxito.")
    else:
        print("\nNo se pudo añadir el contenido de ejemplo.")
        sys.exit(1)
