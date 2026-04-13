import requests
import os
from dotenv import load_dotenv

def discover_ruka():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    ruka_id = os.getenv("RUKA_API_ID")
    ruka_key = os.getenv("RUKA_API_KEY")
    
    headers = {
        "x-api-id": ruka_id,
        "x-api-key": ruka_key,
        "Accept": "application/json"
    }

    # Probar diferentes variaciones de URL para Ruka/Suplait
    urls = [
        "https://api.ruka.ai/v1/purchases",
        "https://api.ruka.ai/v1/expenses",
        "https://suplait.cl/api/v1/purchases",
        "https://www.suplait.cl/api/v1/purchases",
        "https://app.ruka.ai/api/v1/purchases"
    ]
    
    print("🕵️ Buscando el JSON de Gastos (Ruka/Suplait)...")
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            content_type = r.headers.get("Content-Type", "")
            print(f"📡 {url} -> {r.status_code} ({content_type})")
            if r.status_code == 200 and "application/json" in content_type:
                print(f"      ✅ ¡ENCONTRADO! {r.text[:100]}")
        except Exception as e:
            print(f"      ❌ Error en {url}: {e}")

if __name__ == "__main__":
    discover_ruka()
