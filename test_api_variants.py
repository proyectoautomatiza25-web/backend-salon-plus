import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from datetime import date

def test_api_variants():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    secret = "Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC"
    account_id = "191473"
    full_id = "MDAwMDI6MTkxNDcz"
    today = date.today().isoformat()
    
    headers_base = {"Accept": "application/json"}
    
    variants = [
        # Variante 1: Basic Auth con ID Corto
        {"name": "Basic Auth (Short ID)", "auth": HTTPBasicAuth(account_id, secret), "headers": headers_base},
        # Variante 2: Basic Auth con ID Largo
        {"name": "Basic Auth (Long ID)", "auth": HTTPBasicAuth(full_id, secret), "headers": headers_base},
        # Variante 3: Header Personalizado
        {"name": "Fudo-Api-Key Header", "auth": None, "headers": {**headers_base, "X-Fudo-Api-Key": secret}},
        # Variante 4: Token en Header Authorization simple
        {"name": "Auth Token Header", "auth": None, "headers": {**headers_base, "Authorization": secret}}
    ]

    print(f"🕵️‍♂️ Probando Variantes de Conexión para Kingdom Coffee...")

    for v in variants:
        print(f"📡 Intentando {v['name']}...", end=" ")
        try:
            url = f"https://api.fu.do/sales?from={today}&to={today}"
            r = requests.get(url, auth=v['auth'], headers=v['headers'], timeout=8)
            print(f"-> {r.status_code}")
            if r.status_code == 200:
                print(f"✅ ¡INFILTRACIÓN EXITOSA CON {v['name']}!")
                with open("c:/Users/Lenovo/clod database/fudo_data_dump/api_success.json", "w") as f:
                    json.dump({"variant": v['name'], "data": r.json()}, f)
                return True
        except:
            print("💥 Error")

    return False

if __name__ == "__main__":
    test_api_variants()
