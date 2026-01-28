import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

# Credenciales desde tu imagen
CLIENT_ID = "MDAwMDI6MTkxNDcz"
CLIENT_SECRET = "DbJcsn8gNJYI3IOMwVmkMUCx"

# URLs probables de la API de Fudo
BASE_URL_V1 = "https://api.fu.do"
# A veces es específico por region, pero probaremos la global primero

def test_connection():
    print(f"🔌 Intentando conectar a Fudo con Client ID: {CLIENT_ID[:5]}...")

    # Headers comunes
    headers = {
        "User-Agent": "FocusApp/1.0",
        "Accept": "application/json"
    }

    # Endpoint de prueba: Ventas del día (o Customers/Products que suelen estar abiertos)
    # Probamos endpoint de '/sales' (Ventas)
    
    try:
        # Autenticación Basic Auth es el estándar para estos ClientID/Secret
        print("\n1. Probando GET /sales (Ventas recientes)...")
        response = requests.get(
            f"{BASE_URL_V1}/sales", 
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            headers=headers
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Muestra un resumen de lo que encontró
            count = len(data) if isinstance(data, list) else "N/A"
            print(f"   ✅ ¡Éxito! Conexión establecida.")
            print(f"   📊 Se encontraron {count} registros de ventas.")
            if count > 0 and isinstance(data, list):
                print(f"   📝 Ejemplo de venta: ID {data[0].get('id', 'N/A')} - Total: {data[0].get('total', 'N/A')}")
                # Guardamos una muestra para analizar la estructura
                with open("fudo_sample_sales.json", "w", encoding="utf-8") as f:
                    json.dump(data[:1], f, indent=2)
                print("   📁 Se guardó 'fudo_sample_sales.json' con un ejemplo para análisis.")
            return True
        else:
            print(f"   ❌ Error: {response.text}")

    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")

    # Intento 2: Products (a veces las ventas están vacías pero productos no)
    try:
        print("\n2. Probando GET /products (Productos)...")
        response = requests.get(
            f"{BASE_URL_V1}/products", 
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            headers=headers
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ ¡Éxito al leer productos!")
            print(f"   📦 Se encontraron {len(data) if isinstance(data, list) else 'N/A'} productos.")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")

    return False

if __name__ == "__main__":
    test_connection()
