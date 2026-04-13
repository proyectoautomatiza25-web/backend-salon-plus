import requests
import os
from dotenv import load_dotenv

def test_endpoints():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_id = os.getenv("RUKA_API_ID")
    api_key = os.getenv("RUKA_API_KEY")
    
    headers = {
        "x-api-id": api_id,
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    # Endpoints de Ruka que suelen funcionar
    endpoints = [
        "https://www.ruka.ai/api/v1/me",
        "https://www.ruka.ai/api/v1/documents",
        "https://www.ruka.ai/api/v1/purchases",
        "https://www.ruka.ai/api/v1/expenses"
    ]
    
    print("🧪 Probando RUKA...")
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"   {url} -> {r.status_code}")
            if r.status_code == 200:
                print(f"      OK! Muestra: {str(r.json())[:100]}")
        except Exception as e:
            print(f"      Error: {e}")

if __name__ == "__main__":
    test_endpoints()
