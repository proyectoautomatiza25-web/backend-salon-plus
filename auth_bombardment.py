import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from datetime import date

def final_auth_bombardment():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    key = "MzZAMTkxNDcz"
    secret = "Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC"
    today = date.today().isoformat()
    
    url = f"https://api.fu.do/sales?from={today}&to={today}"
    
    variants = [
        {"name": "X-API-KEY Header", "headers": {"X-API-KEY": secret, "Accept": "application/json"}},
        {"name": "X-Fudo-Access-Token", "headers": {"X-Fudo-Access-Token": secret, "Accept": "application/json"}},
        {"name": "Authorization Bearer Secret", "headers": {"Authorization": f"Bearer {secret}", "Accept": "application/json"}},
        {"name": "Authorization Basic (Both)", "auth": HTTPBasicAuth(key, secret), "headers": {"Accept": "application/json"}},
        {"name": "Custom Header Fudo", "headers": {"X-Fudo-Api-Key": f"{key}:{secret}", "Accept": "application/json"}}
    ]

    print("🚀 BOMBARDEANDO FUDO CON NUEVAS LLAVES VIP...")

    for v in variants:
        print(f"📡 Probando {v['name']}...", end=" ")
        try:
            auth = v.get("auth")
            r = requests.get(url, headers=v['headers'], auth=auth, timeout=8)
            print(f"-> {r.status_code}")
            if r.status_code == 200:
                print(f"✅ ¡INFILTRACIÓN EXITOSA! Puerta encontrada: {v['name']}")
                return True
        except:
            print("💥 Error")

    # TEST RAPIDO DE PRODUCTOS (A ver si esa llave es solo para lectura de carta)
    print("📦 Probando llave en /products...", end=" ")
    r_prod = requests.get("https://api.fu.do/products", auth=HTTPBasicAuth(key, secret), timeout=5)
    print(f"-> {r_prod.status_code}")

    return False

if __name__ == "__main__":
    final_auth_bombardment()
