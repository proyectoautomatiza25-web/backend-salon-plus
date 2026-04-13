
import asyncio
import os
import httpx
from datetime import date, timedelta
from dotenv import load_dotenv
from app.integrations.fudo_client import FudoClient

async def debug_auth_and_sales():
    load_dotenv()
    client = FudoClient()
    
    print("Intentando refrescar token...")
    new_token = await client.refresh_token()
    if new_token:
        print(f"Token refrescado exitosamente: {new_token[:20]}...")
    else:
        print("Fallo al refrescar token. Verificando Client ID/Secret...")
        print(f"ID: {client.client_id}")
        print(f"Secret: {client.client_secret}")

    # Probar conexión básica
    test = await client.test_connection()
    print(f"Test Connection: {test}")

    # Rango de fechas
    hoy = date.today()
    desde = hoy - timedelta(days=7)
    
    headers = client.get_auth_headers()
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        url = f"{client.base_url}/sales"
        params = {"from": desde.isoformat(), "to": hoy.isoformat()}
        r = await http_client.get(url, headers=headers, params=params)
        
        print(f"Sales Request Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Ventas encontradas: {len(data)}")
        else:
            print(f"Sales Request Error: {r.text}")

if __name__ == "__main__":
    asyncio.run(debug_auth_and_sales())
