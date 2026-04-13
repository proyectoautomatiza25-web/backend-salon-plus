import asyncio
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

async def brute_probe_v2():
    load_dotenv()
    client_id = os.getenv("FUDO_CLIENT_ID")
    client_secret = os.getenv("FUDO_CLIENT_SECRET")
    
    # Probamos la ruta oficial de ventas pero sin filtros de hora, solo fecha
    url = "https://api.fu.do/sales"
    params = {"from": "2026-04-08", "to": "2026-04-08"}
    
    print(f"--- Probando conexion con ID: {client_id} ---")
    
    auth = HTTPBasicAuth(client_id, client_secret)
    headers = {"Accept": "application/json"}
    
    r = requests.get(url, auth=auth, headers=headers, params=params)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        sales = data.get('data', data)
        if isinstance(sales, dict): sales = list(sales.values())
        
        print(f"Ventas crudas obtenidas: {len(sales)}")
        for s in sales[:20]:
            num = s.get('number')
            total = s.get('total')
            print(f" - Venta #{num}: Total ${total} | ID: {s.get('id')}")
            if str(num) == "5982":
                print("!!! ENCONTRADA !!!")

if __name__ == "__main__":
    asyncio.run(brute_probe_v2())
