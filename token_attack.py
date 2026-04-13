import requests
import json
import os
from dotenv import load_dotenv

def fudo_token_attack():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    client_id = os.getenv("FUDO_CLIENT_ID")
    client_secret = os.getenv("FUDO_CLIENT_SECRET")
    
    # El endpoint secreto para convertir Keys en Tokens
    url = "https://api.fu.do/oauth/token"
    
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    print("🔓 Intentando generar TOKEN DE ACCESO OAUTH2...")
    print(f"ID: {client_id}")
    
    try:
        r = requests.post(url, data=payload, timeout=10)
        print(f"📡 STATUS: {r.status_code}")
        
        if r.status_code == 200:
            token_data = r.json()
            access_token = token_data.get("access_token")
            print("✅ ¡EXITO! Token de Acceso Admin generado.")
            # Guardamos el token real
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/oauth_token.json", "w") as f:
                json.dump(token_data, f)
            return True
        else:
            print(f"❌ Error: {r.text}")
            # Si falla, probamos con el formato JSON
            print("🔄 Reintentando con formato JSON payload...")
            r2 = requests.post(url, json=payload, timeout=10)
            print(f"📡 STATUS (JSON): {r2.status_code}")
            if r2.status_code == 200:
                print("✅ ¡EXITO CON JSON!")
                return True
    except Exception as e:
        print(f"💥 Error: {e}")
        
    return False

if __name__ == "__main__":
    fudo_token_attack()
