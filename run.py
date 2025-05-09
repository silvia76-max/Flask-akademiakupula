from app import create_app, db
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Creando aplicación Flask")
app = create_app()

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask")
    app.run(debug=True, host='0.0.0.0', port=5000)
