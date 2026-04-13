import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from datetime import date

def test_official_key():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    client_id = os.getenv("FUDO_CLIENT_ID")
    client_secret = os.getenv("FUDO_CLIENT_SECRET")
    today = date.today().isoformat()
    
    auth = HTTPBasicAuth(client_id, client_secret)
    headers = {"Accept": "application/json"}
    
    print(f"🚀 Probando LLAVE MAESTRA para Kingdom Coffee...")
    print(f"ID: {client_id}")
    
    # Probamos el endpoint de ventas oficial
    url = f"https://api.fu.do/sales?from={today}&to={today}"
    
    try:
        r = requests.get(url, auth=auth, headers=headers, timeout=10)
        print(f"📡 STATUS: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            items = data.get('data', data)
            if isinstance(items, dict): items = list(items.values())
            
            total = sum(float(s.get('amount', 0)) for s in items)
            print(f"✅ ¡EXITO TOTAL! Ventas de hoy encontradas.")
            print(f"💰 TOTAL REAL DE HOY: ${total}")
            
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/official_sales_today.json", "w") as f:
                json.dump({"total": total, "count": len(items), "data": items}, f)
            return True
        else:
            print(f"❌ Error: {r.text}")
    except Exception as e:
        print(f"💥 Fallo crítico: {e}")
        
    return False

if __name__ == "__main__":
    test_official_key()
