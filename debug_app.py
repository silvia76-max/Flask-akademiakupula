"""
Script para ejecutar la aplicación en modo depuración y capturar errores.
"""

import sys
import logging
from app import create_app

# Configurar logging para mostrar en consola
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    logger.info("Iniciando aplicación en modo depuración...")
    app = create_app()
    
    # Configurar para mostrar errores detallados
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Ejecutar la aplicación
    app.run(debug=True, use_reloader=False)
except Exception as e:
    logger.error(f"Error al iniciar la aplicación: {str(e)}", exc_info=True)
