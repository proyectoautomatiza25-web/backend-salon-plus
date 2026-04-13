import requests
import json
import os
from dotenv import load_dotenv

def extract_real_sales_from_cash():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/"
    }

    # Ahora vamos a la accion: Pedir el resumen de la caja 1
    # Probablemente se necesite un resumen o reporte de cierre
    url = "https://api.fu.do/cash_registers/1/summaries" # Suponiendo esta ruta por los patterns anteriores
    
    print("💰 Extrayendo TOTAL DE CAJA de hoy...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"📡 {url} -> {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # Guardamos el tesoro
            with open("caja_final_real.json", "w") as f:
                json.dump(data, f)
            print("✅ ¡TENEMOS EL DINERO REAL!")
            return data
    except:
        pass
    return None

if __name__ == "__main__":
    extract_real_sales_from_cash()
