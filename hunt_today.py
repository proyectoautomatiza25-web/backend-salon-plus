import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def hunt_todays_money():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    today = date.today().isoformat()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "fudo-country-code": "CL",
        "fudo-invoicing-provider": "sii"
    }

    # Buscamos las boletas que se estan emitiendo AHORA (sale_receipts)
    url = f"https://api.fu.do/sale_receipts?from={today}&to={today}"
    
    print(f"🧾 Buscando Boletas de HOY ({today})...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"📡 {url} -> {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get('data', data)
            if isinstance(items, dict): items = list(items.values())
            
            total = sum(b.get('total', 0) for b in items)
            print(f"✅ ¡ENCONTRADO! Total Boleteado Hoy: ${total}")
            
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/today_money_real.json", "w") as f:
                json.dump({"total": total, "receipts": items}, f)
            return total
    except:
        pass
    return 0

if __name__ == "__main__":
    hunt_todays_money()
