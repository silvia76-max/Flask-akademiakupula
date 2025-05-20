"""
Script para probar la API de Flask directamente.
"""

import requests
import json
import sys

def test_ping():
    """Prueba el endpoint /api/test/ping"""
    print("\n=== Probando /api/test/ping ===")
    try:
        response = requests.get('http://localhost:5000/api/test/ping')
        print(f"Status: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_cors():
    """Prueba el endpoint /api/test/cors-test"""
    print("\n=== Probando /api/test/cors-test ===")
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = requests.get('http://localhost:5000/api/test/cors-test', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_cursos():
    """Prueba el endpoint /api/cursos"""
    print("\n=== Probando /api/cursos/ ===")
    try:
        response = requests.get('http://localhost:5000/api/cursos/')
        print(f"Status: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_options():
    """Prueba una solicitud OPTIONS"""
    print("\n=== Probando OPTIONS /api/test/ping ===")
    try:
        response = requests.options('http://localhost:5000/api/test/ping', headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        })
        print(f"Status: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Función principal"""
    print("Iniciando pruebas de la API...")

    # Probar ping
    ping_success = test_ping()

    # Probar CORS
    cors_success = test_cors()

    # Probar cursos
    cursos_success = test_cursos()

    # Probar OPTIONS
    options_success = test_options()

    # Resumen
    print("\n=== Resumen ===")
    print(f"Ping: {'✅ OK' if ping_success else '❌ Error'}")
    print(f"CORS: {'✅ OK' if cors_success else '❌ Error'}")
    print(f"Cursos: {'✅ OK' if cursos_success else '❌ Error'}")
    print(f"OPTIONS: {'✅ OK' if options_success else '❌ Error'}")

    # Resultado final
    if ping_success and cors_success and cursos_success and options_success:
        print("\n✅ Todas las pruebas pasaron correctamente.")
        return 0
    else:
        print("\n❌ Algunas pruebas fallaron.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
