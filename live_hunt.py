import requests
import json
import os
from dotenv import load_dotenv

def search_live_sales():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do"
    }

    # El asalto por busqueda POST (mas potente)
    url = "https://api.fu.do/sales/search"
    payload = {
        "from": "2026-02-06T00:00:00-03:00",
        "to": "2026-02-06T23:59:59-03:00",
        "per_page": 50
    }
    
    print("🕵️‍♂️ Iniciando BUSQUEDA DE VENTAS LIVE (POST /sales/search)...")
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=12)
        print(f"📡 {url} -> {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get('data', data)
            print(f"✅ ¡BOTÍN ENCONTRADO! {len(items)} ventas detectadas.")
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/live_sales_hunt.json", "w") as f:
                json.dump(data, f)
            return data
    except:
        pass
    return None

if __name__ == "__main__":
    search_live_sales()
