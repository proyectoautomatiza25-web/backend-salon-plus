import requests
import json
import os
from dotenv import load_dotenv
from datetime import date, timedelta

def hack_yesterday_sales():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    # Este es el token que logramos extraer anoche del navegador del usuario
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    # Ayer
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "fudo-country-code": "CL"
    }

    url = f"https://api.fu.do/sales?from={yesterday}&to={yesterday}"
    
    print(f"🕵️‍♂️ Intentando recuperar ventas de AYER ({yesterday}) via Session Hack...")
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"📡 STATUS: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            items = data.get('data', data)
            if isinstance(items, dict): items = list(items.values())
            
            total = sum(float(s.get('amount', 0)) for s in items)
            print(f"✅ ¡EXITO TOTAL! Ventas de ayer recuperadas.")
            print(f"💰 TOTAL AYER: ${total}")
            
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/yesterday_sales_hack.json", "w") as f:
                json.dump({"total": total, "detalles": items}, f)
            return True
        else:
            print(f"❌ Error: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"💥 Error: {e}")
            
    return False

if __name__ == "__main__":
    hack_yesterday_sales()
