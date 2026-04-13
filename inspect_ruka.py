import requests
import os
from dotenv import load_dotenv

def inspect_ruka_response():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_id = os.getenv("RUKA_API_ID")
    api_key = os.getenv("RUKA_API_KEY")
    
    url = "https://www.ruka.ai/api/v1/me"
    headers = {
        "x-api-id": api_id,
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    print(f"📡 Llamando a Ruka /me...")
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Content Type: {r.headers.get('Content-Type')}")
    print(f"Body: {r.text[:500]}")

if __name__ == "__main__":
    inspect_ruka_response()
