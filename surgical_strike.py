import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from datetime import date

def surgical_strike():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    # Decodificado: MzZAMTkxNDcz -> 36@191473
    user_plain = "36@191473"
    secret = "Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC"
    today = date.today().isoformat()
    
    # Probamos varios endpoints con los datos limpios
    targets = [
        "https://api.fu.do/account/me",
        f"https://api.fu.do/sales?from={today}&to={today}",
        "https://api.fu.do/products?per_page=1"
    ]
    
    print(f"🕵️‍♂️ INICIANDO ATAQUE QUIRÚRGICO (User: {user_plain})...")
    
    for url in targets:
        print(f"📡 Probando {url}...", end=" ")
        try:
            # Fudo suele usar Basic Auth con estos datos
            r = requests.get(url, auth=HTTPBasicAuth(user_plain, secret), timeout=10)
            print(f"-> {r.status_code}")
            
            if r.status_code == 200:
                print(f"✅ ¡ACCESO TOTAL CONCEDIDO EN {url}!")
                with open("c:/Users/Lenovo/clod database/fudo_data_dump/surgical_success.json", "w") as f:
                    json.dump(r.json(), f)
                return True
        except Exception as e:
            print(f"💥 Error: {e}")
            
    return False

if __name__ == "__main__":
    surgical_strike()
