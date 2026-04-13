import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

def ultimate_fudo_scrape():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "fudo-country-code": "CL"
    }

    base_url = "https://api.fu.do"
    results = {}

    # Endpoints que vimos con 200 en tus capturas
    endpoints = [
        "sale_identifiers",
        "summaries",
        "customers",
        "sale_reports",
        "v2/sales",
        "v2/orders",
        "v2/summaries"
    ]

    print("🕵️‍♂️ Iniciando escaneo profundo de Kingdom Coffee...")

    for ep in endpoints:
        url = f"{base_url}/{ep}"
        print(f"📡 Intentando con {url}...")
        try:
            # Primero intentamos GET
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                print(f"   ✅ ¡EXITO EN {ep}!")
                results[ep] = r.json()
            elif r.status_code == 405: # Method not allowed, probamos POST
                r_post = requests.post(url, headers=headers, json={}, timeout=10)
                if r_post.status_code == 200:
                    print(f"   ✅ ¡EXITO EN {ep} (POST)!")
                    results[ep] = r_post.json()
        except Exception as e:
            print(f"   ❌ Error en {ep}: {str(e)}")

    # Si encontramos sale_identifiers, intentamos bajar los detalles de las ultimas 10 ventas
    if "sale_identifiers" in results:
        ids = results["sale_identifiers"]
        if isinstance(ids, dict): ids = list(ids.values())
        if isinstance(ids, list) and len(ids) > 0:
            print(f"🛒 Detectadas {len(ids)} ventas recientes. Bajando detalles...")
            sales_details = []
            for item in ids[:10]:
                sale_id = item.get('id') if isinstance(item, dict) else item
                if sale_id:
                    s_url = f"{base_url}/sales/{sale_id}"
                    sr = requests.get(s_url, headers=headers, timeout=5)
                    if sr.status_code == 200:
                        sales_details.append(sr.json())
            results["recent_sales_details"] = sales_details

    # Guardar todo el volcado
    with open("c:/Users/Lenovo/clod database/fudo_data_dump/super_hack_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Escaneo completado. Se encontraron {len(results)} fuentes de datos nuevas.")

if __name__ == "__main__":
    ultimate_fudo_scrape()
