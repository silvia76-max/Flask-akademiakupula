from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

test_bp = Blueprint('test', __name__)

@test_bp.route('/ping', methods=['GET'])
def ping():
    # Log the request headers for debugging
    logger.info(f"Request headers: {dict(request.headers)}")

    # Return a simple response
    return jsonify({
        "success": True,
        "message": "pong desde Blueprint!",
        "data": {
            "cors_test": "success",
            "headers_received": dict(request.headers)
        }
    })

@test_bp.route('/cors-test', methods=['GET', 'POST', 'OPTIONS'])
def cors_test():
    """
    Endpoint para probar la configuración de CORS.
    Este endpoint devuelve información sobre la solicitud recibida,
    incluyendo los encabezados, el método y el origen.
    """
    # Log the request for debugging
    logger.info(f"CORS test request received: {request.method} from {request.headers.get('Origin')}")
    logger.info(f"Request headers: {dict(request.headers)}")

    # Return information about the request
    return jsonify({
        "success": True,
        "message": "CORS test successful",
        "data": {
            "method": request.method,
            "origin": request.headers.get('Origin'),
            "headers": dict(request.headers)
        }
    })
