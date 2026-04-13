"""
Prueba de Whapi para ver si el canal está activo.
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN")

def test_whapi():
    url = "https://gate.whapi.cloud/health"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {WHAPI_TOKEN}"
    }
    
    print(f"Testing Whapi...")
    try:
        r = requests.get(url, headers=headers)
        print(f"Health Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Body: {r.json()}")
            
        # Probar settings para ver el número
        r2 = requests.get("https://gate.whapi.cloud/settings", headers=headers)
        print(f"Settings Status: {r2.status_code}")
        if r2.status_code == 200:
            print(f"Settings: {r2.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_whapi()
