import requests
import os
from dotenv import load_dotenv
import json
from datetime import date

def force_real_data():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    today = date.today().isoformat()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/"
    }

    # Basado en tu captura uploaded_media_3 que dio 200 OK en 'summaries'
    endpoints = [
        f"https://api.fu.do/summaries?from={today}&to={today}",
        f"https://api.fu.do/summaries",
        f"https://api.fu.do/cash_registers",
        f"https://api.fu.do/account",
        f"https://api.fu.do/v2/summaries?date={today}"
    ]
    
    print(f"🎯 INTENTANDO ACCESO REAL A CAJA (Día: {today})...")
    
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"📡 {url} -> {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"✅ ¡LO TENEMOS! Datos reales encontrados.")
                # Guardamos para procesar en el dashboard
                with open("fudo_real_caja.json", "w") as f:
                    json.dump(data, f)
                return True
        except:
            pass
    return False

if __name__ == "__main__":
    force_real_data()
