import requests
import os
from dotenv import load_dotenv

def try_all_ruka_domains():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_id = os.getenv("RUKA_API_ID")
    api_key = os.getenv("RUKA_API_KEY")
    
    headers = {
        "x-api-id": api_id,
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    domains = [
        "https://api.ruka.ai/v1/purchases",
        "https://www.ruka.cl/api/v1/purchases",
        "https://app.ruka.cl/api/v1/purchases",
        "https://api.suplait.cl/v1/purchases",
        "https://app.suplait.cl/api/v1/purchases",
        "https://ruka.ai/api/v1/me"
    ]
    
    print("🕵️ Explorando dominios de Ruka/Suplait con tus llaves...")
    for url in domains:
        try:
            r = requests.get(url, headers=headers, timeout=8)
            print(f"📡 {url} -> {r.status_code}")
            if r.status_code == 200:
                ct = r.headers.get("Content-Type", "")
                if "application/json" in ct:
                    print(f"   ✅ ¡BINGO! Respuesta JSON: {r.text[:100]}")
                    return
                else:
                    print(f"   ⚠️ Retornó HTML (Login/Redirect)")
        except Exception as e:
            print(f"   ❌ Fallo: {e}")

if __name__ == "__main__":
    try_all_ruka_domains()
