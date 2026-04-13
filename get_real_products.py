import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

def get_real_products():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    url = "https://api.fu.do/products"
    print(f"📦 Extrayendo productos reales de Kingdom Coffee...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Fudo v2 extrae los productos en un dict con IDs como llaves
            prods = data.get('data', data)
            if isinstance(prods, dict):
                prods = list(prods.values())
            
            # Guardamos los primeros 10 para el Dashboard
            clean_prods = []
            for p in prods[:10]:
                clean_prods.append({
                    "nombre": p.get('name'),
                    "precio": p.get('price'),
                    "categoria": "General"
                })
            
            with open("real_products_kingdom.json", "w", encoding="utf-8") as f:
                json.dump(clean_prods, f, indent=2)
            print(f"✅ ¡Éxito! {len(clean_prods)} productos reales listos.")
            return clean_prods
    except Exception as e:
        print(f"❌ Error: {e}")
    return []

if __name__ == "__main__":
    get_real_products()
