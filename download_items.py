import requests
import json
import os
from dotenv import load_dotenv

def download_items_official():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_key = os.getenv("FUDO_CLIENT_ID")
    api_secret = os.getenv("FUDO_CLIENT_SECRET")
    
    # 1. Obtener Token
    r_auth = requests.post("https://auth.fu.do/api", json={"apiKey": api_key, "apiSecret": api_secret}, timeout=10)
    if r_auth.status_code != 200: return
    token = r_auth.json().get("token")
    
    # 2. Descargar Items (v1alpha1)
    url = "https://api.fu.do/v1alpha1/items"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    print("📦 Descargando catálogo de Items (nombres para el ranking)...")
    r = requests.get(url, headers=headers, params={"page[size]": 500}, timeout=20)
    if r.status_code == 200:
        data = r.json()
        items = data if isinstance(data, list) else data.get('data', [])
        
        with open("c:/Users/Lenovo/clod database/fudo_data_dump/items.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False)
        print(f"✅ {len(items)} items guardados.")

if __name__ == "__main__":
    download_items_official()
