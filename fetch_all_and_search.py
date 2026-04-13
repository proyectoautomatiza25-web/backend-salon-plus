import requests
import os
import json
from dotenv import load_dotenv

def get_everything_from_fudo():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/"
    }
    
    # 1. Traer TODOS los productos
    prods_url = "https://api.fu.do/products"
    print("📦 Extrayendo TODA la carta de Kingdom Coffee...")
    try:
        r = requests.get(prods_url, headers=headers)
        if r.status_code == 200:
            all_prods = r.json().get('data', r.json())
            if isinstance(all_prods, dict): 
                all_prods = list(all_prods.values())
            
            with open("all_products_real.json", "w", encoding="utf-8") as f:
                json.dump(all_prods, f, indent=2)
            print(f"✅ ¡ÉXITO! He bajado {len(all_prods)} productos reales.")
            
            # 2. Intentar buscar ventas vía POST (el truco del 500)
            print("💰 Intentando forzar el reporte de ventas real...")
            search_url = "https://api.fu.do/sales/search"
            payload = {"from": "2026-02-05", "to": "2026-02-05", "per_page": 50}
            r_sales = requests.post(search_url, headers=headers, json=payload)
            if r_sales.status_code == 200:
                print("✅ ¡BINGO! Ventas reales obtenidas vía búsqueda.")
                with open("real_sales_found.json", "w") as f:
                    json.dump(r_sales.json(), f)
            else:
                print(f"❌ Ventas siguen bloqueadas ({r_sales.status_code})")
    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    get_everything_from_fudo()
