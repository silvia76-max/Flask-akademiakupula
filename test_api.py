"""
Script para probar directamente la API.
"""

import requests
import json

def test_api():
    """Prueba directamente la API."""
    base_url = "http://localhost:5000"
    
    # Datos de prueba
    test_user = {
        "full_name": "Usuario Test",
        "postal_code": "28001",
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Probar endpoint de test
    print("\n1. Probando endpoint de test...")
    try:
        response = requests.get(f"{base_url}/api/test")
        print(f"Respuesta: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Probar registro
    print("\n2. Probando registro...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=test_user
        )
        print(f"Respuesta: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 201:
            token = response.json().get("data", {}).get("access_token")
            print(f"Token obtenido: {token}")
        else:
            print("No se pudo obtener token")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Probar login
    print("\n3. Probando login...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        print(f"Respuesta: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            token = response.json().get("data", {}).get("access_token")
            print(f"Token obtenido: {token}")
            
            # Probar perfil
            print("\n4. Probando perfil...")
            try:
                response = requests.get(
                    f"{base_url}/api/auth/profile",
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"Respuesta: {response.status_code}")
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"Error: {str(e)}")
        else:
            print("No se pudo obtener token")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Probar contacto
    print("\n5. Probando contacto...")
    try:
        response = requests.post(
            f"{base_url}/api/contacto",
            json={
                "nombre": test_user["full_name"],
                "email": test_user["email"],
                "telefono": "612345678",
                "curso": "maquillaje",
                "mensaje": "Mensaje de prueba desde test_api.py"
            }
        )
        print(f"Respuesta: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()
