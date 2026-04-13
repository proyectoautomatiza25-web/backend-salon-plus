
import asyncio
import os
import httpx
import json
from datetime import date, timedelta
from dotenv import load_dotenv
from app.integrations.fudo_client import FudoClient

async def debug_sales_structure():
    load_dotenv()
    client = FudoClient()
    await client.refresh_token()
    
    hoy = date.today()
    desde = hoy - timedelta(days=7)
    
    headers = client.get_auth_headers()
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        url = f"{client.base_url}/sales"
        params = {"from": desde.isoformat(), "to": hoy.isoformat()}
        r = await http_client.get(url, headers=headers, params=params)
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                items = list(data.values())
            else:
                items = data
            
            print(f"Encontrados {len(items)} items.")
            if items:
                print("Estructura de la primera venta:")
                print(json.dumps(items[0], indent=2))
        else:
            print(f"Error: {r.status_code} - {r.text}")

if __name__ == "__main__":
    asyncio.run(debug_sales_structure())
