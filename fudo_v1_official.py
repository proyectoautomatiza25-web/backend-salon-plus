import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def get_official_fudo_token():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_key = os.getenv("FUDO_CLIENT_ID")
    api_secret = os.getenv("FUDO_CLIENT_SECRET")
    
    auth_url = "https://auth.fu.do/api"
    payload = {
        "apiKey": api_key,
        "apiSecret": api_secret
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    print("🔐 Intentando obtener Token Oficial (v1alpha1)...")
    try:
        r = requests.post(auth_url, json=payload, headers=headers, timeout=10)
        print(f"📡 Status: {r.status_code}")
        if r.status_code == 200:
            token_data = r.json()
            token = token_data.get("token")
            print("✅ Token obtenido exitosamente.")
            
            # Guardamos el token en el .env o en un archivo temporal
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/official_v1_token.json", "w") as f:
                json.dump(token_data, f)
            return token
        else:
            print(f"❌ Error en autenticación: {r.text}")
    except Exception as e:
        print(f"💥 Error crítico: {e}")
    return None

def fetch_sales_v1(token):
    today = date.today().isoformat()
    # Según docs, el filtro es filter[createdAt]=and(gte.2020-05-11T00:00:00Z,lte.2020-05-11T23:59:59Z)
    start_time = f"{today}T00:00:00Z"
    end_time = f"{today}T23:59:59Z"
    
    url = "https://api.fu.do/v1alpha1/sales"
    params = {
        "page[size]": 500,
        "filter[createdAt]": f"and(gte.{start_time},lte.{end_time})"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    print(f"💰 Consultando ventas de hoy ({today})...")
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"📡 Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            sales = data if isinstance(data, list) else data.get('data', [])
            total = sum(float(s.get('total', 0)) for s in sales)
            print(f"✅ ¡Éxito! Total de ventas hoy: ${total}")
            
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/real_v1_sales.json", "w") as f:
                json.dump({"total": total, "count": len(sales), "data": sales}, f)
            return total
        else:
            print(f"❌ Error al obtener ventas: {r.text}")
    except Exception as e:
        print(f"💥 Error: {e}")
    return 0

if __name__ == "__main__":
    token = get_official_fudo_token()
    if token:
        fetch_sales_v1(token)
