import requests
import json
import os
from dotenv import load_dotenv

def hunt_sii_boletas():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "fudo-country-code": "CL",
        "fudo-invoicing-provider": "sii"
    }

    # Intentamos la ruta de RECEIPTS (Boletas emitidas)
    url = "https://api.fu.do/sale_receipts?per_page=10"
    
    print("🧾 Buscando Boletas Electrónicas del SII...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"📡 {url} -> {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            total_emitido = 0
            # Sumar montos de las boletas reales
            items = data.get('data', data)
            if isinstance(items, dict): items = list(items.values())
            
            for b in items:
                monto = b.get('total', 0)
                total_emitido += monto
            
            print(f"✅ ¡BINGO! Boletas encontradas. Total emitido: ${total_emitido}")
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/sii_boletas.json", "w") as f:
                json.dump(data, f)
            return total_emitido
    except:
        pass
    return 0

if __name__ == "__main__":
    hunt_sii_boletas()
