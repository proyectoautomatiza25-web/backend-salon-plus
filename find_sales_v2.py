import requests
import json
import os
from dotenv import load_dotenv

def find_sales_endpoint():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/"
    }

    # Intentamos encontrar el endpoint real que usa la v2 para el Dashboard
    endpoints = [
        "https://api.fu.do/v2/summaries?from=2026-02-05&to=2026-02-06",
        "https://api.fu.do/v2/sales?per_page=5",
        "https://api.fu.do/v2/dashboard/stats",
        "https://api.fu.do/sale_reports/daily",
        "https://api.fu.do/v2/accounts/191473/summaries"
    ]
    
    print("🎯 Buscando el monto real de ventas...")
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"📡 {url} -> {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"      ✅ ¡ENCONTRADO! Respuesta: {json.dumps(data)[:300]}")
                return data
        except:
            pass
    return None

if __name__ == "__main__":
    find_sales_endpoint()
