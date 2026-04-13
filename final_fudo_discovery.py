import requests
import json
import os
from dotenv import load_dotenv

def final_discovery():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Estos son los endpoints mas probables para sacar el TOTAL de ventas
    endpoints = [
        "https://api.fu.do/sale_summaries",
        "https://api.fu.do/dashboard/stats",
        "https://api.fu.do/reports/sales",
        "https://api.fu.do/v2/sales",
        "https://api.fu.do/sale_identifiers", # Este lo vimos en tu captura
        "https://api.fu.do/account/me"
    ]
    
    print("🔍 Buscando el grifo de VENTAS...")
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"📡 {url} -> {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"   ✅ ¡ENCONTRADO! Muestra: {str(data)[:200]}")
                # Guardamos lo que sea que funcione para usarlo en el Dashboard
                with open("fudo_discovery_success.json", "w") as f:
                    json.dump({"url": url, "sample": data}, f)
        except Exception as e:
            print(f"   ❌ Error en {url}: {e}")

if __name__ == "__main__":
    final_discovery()
