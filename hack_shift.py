import requests
import json
import os
from dotenv import load_dotenv

def hack_current_shift_money():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do"
    }

    # Intentamos entrar al reporte del Turno 3 (que es el de hoy segun el dump)
    target_id = 3
    url = f"https://api.fu.do/shifts/{target_id}/summaries" 
    
    print(f"💰 Intentando extraer el dinero del TURNO {target_id} AM...")
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"📡 {url} -> {r.status_code}")
        if r.status_code == 200:
            print("✅ ¡EXITO! Hemos entrado a la caja del turno actual.")
            data = r.json()
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/current_shift_money.json", "w") as f:
                json.dump(data, f)
            return data
    except:
        pass
            
    return None

if __name__ == "__main__":
    hack_current_shift_money()
