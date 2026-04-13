import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import base64

def official_handshake_final():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_key = "MzZAMTkxNDcz"
    api_secret = "Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC"
    
    # Intentamos la ruta base de productos que es la más "abierta"
    url = "https://api.fu.do/products?per_page=1"
    
    # Generamos el Base64 manual por si acaso
    auth_str = f"{api_key}:{api_secret}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()

    variants = [
        {"name": "Header: X-Fudo-Api-Key", "headers": {"X-Fudo-Api-Key": api_key, "Accept": "application/json"}},
        {"name": "Header: Fudo-Api-Key", "headers": {"Fudo-Api-Key": api_key, "Accept": "application/json"}},
        {"name": "Authorization: <API_KEY>", "headers": {"Authorization": api_key, "Accept": "application/json"}},
        {"name": "Authorization: Basic <B64>", "headers": {"Authorization": f"Basic {auth_b64}", "Accept": "application/json"}},
        {"name": "Authorization: Bearer <API_KEY>", "headers": {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}},
        {"name": "X-API-KEY", "headers": {"X-API-KEY": api_key, "Accept": "application/json"}}
    ]

    print("🚀 PROBANDO APERTURA OFICIAL CON LLAVES ADMIN...")

    for v in variants:
        print(f"📡 Probando {v['name']}...", end=" ", flush=True)
        try:
            r = requests.get(url, headers=v['headers'], timeout=8)
            print(f"-> {r.status_code}")
            if r.status_code == 200:
                print(f"✅ ¡CÓDIGO CORRECTO ENCONTRADO! Usando: {v['name']}")
                # Guardamos como el éxito definitivo
                with open("c:/Users/Lenovo/clod database/fudo_data_dump/official_auth_method.json", "w") as f:
                    json.dump({"method": v['name'], "headers": v['headers']}, f)
                return True
        except Exception as e:
            print(f"💥 Error: {e}")

    return False

if __name__ == "__main__":
    official_handshake_final()
