import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def final_aggressive_harvest():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    today = date.today().isoformat()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "fudo-country-code": "CL",
        "fudo-invoicing-provider": "sii"
    }

    base_url = "https://api.fu.do"
    
    # Intentamos las rutas mas jugosas basadas en lo que el dashboard suele pedir
    targets = [
        f"summaries?from={today}&to={today}",
        f"v2/summaries?from={today}&to={today}",
        "customers?per_page=50",
        "dashboard",
        "v2/dashboard",
        "stats",
        "v2/stats",
        "sale_reports/daily",
        "sale_reports/monthly",
        "inventory_reports/stock",
        "cash_registers/1/summaries"
    ]
    
    print("🏴‍☠️ Iniciando Cosecha de Datos Kingdom Coffee...")
    
    harvest = {}
    for t in targets:
        url = f"{base_url}/{t}"
        print(f"📡 Cosechando {url}...")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                print(f"   ✅ ¡ENCONTRADO! ({len(r.text)} bytes)")
                harvest[t] = r.json()
        except: pass

    # Guardamos todo
    with open("c:/Users/Lenovo/clod database/fudo_data_dump/final_harvest.json", "w", encoding="utf-8") as f:
        json.dump(harvest, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Cosecha terminada. Se encontraron {len(harvest)} nuevas fuentes.")

if __name__ == "__main__":
    final_aggressive_harvest()
