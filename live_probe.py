import requests
import json
import os
from dotenv import load_dotenv

def fudo_live_probe():
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
    
    # BUSCANDO DATOS "VIVOS" (LO QUE ESTA PASANDO AHORA)
    live_targets = [
        "orders",
        "active_sales",
        "sale_identifiers/active",
        "shifts/current",
        "reservations",
        "v2/orders/active"
    ]
    
    print("🕵️‍♂️ Iniciando SCAN LIVE (Buscando lo que pasa ahora mismo)...")
    
    live_data = {}
    for target in live_targets:
        url = f"{base_url}/{target}"
        print(f"📡 Escaneando {target}...", end=" ", flush=True)
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                print(f"✅ ¡VIVO! ({len(r.text)} bytes)")
                live_data[target] = r.json()
            else:
                print(f"❌ {r.status_code}")
        except:
            print("💥 Timeout")

    # Guardar en el dump para el dashboard
    with open("c:/Users/Lenovo/clod database/fudo_data_dump/live_monitor.json", "w", encoding="utf-8") as f:
        json.dump(live_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ Scan finalizado. Se encontraron {len(live_data)} canales activos.")

if __name__ == "__main__":
    fudo_live_probe()
