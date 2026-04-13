"""
Prueba endpoints de Fudo para proveedores y compras.
"""
import asyncio, os
from dotenv import load_dotenv
import httpx

load_dotenv()
FUDO_BASE_URL = os.getenv("FUDO_BASE_URL", "https://api.fu.do").rstrip('/')
FUDO_BEARER_TOKEN = os.getenv("FUDO_BEARER_TOKEN", "")

async def probar_endpoints():
    headers = {
        "Authorization": f"Bearer {FUDO_BEARER_TOKEN}",
        "Accept": "application/json",
        "fudo-country-code": "CL"
    }
    
    endpoints = [
        "/providers",
        "/suppliers",
        "/vendors",
        "/purchases",
        "/purchases/invoices",
        "/inventory/moves",
        "/inventory/stocks"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for ep in endpoints:
            try:
                r = await client.get(f"{FUDO_BASE_URL}{ep}", headers=headers)
                print(f"Endpoint {ep}: {r.status_code}")
                if r.status_code == 200:
                    data = r.json()
                    print(f"  Count: {len(data) if isinstance(data, (list, dict)) else '?'}")
                    if data:
                        # Print first item keys
                        item = list(data.values())[0] if isinstance(data, dict) else data[0]
                        print(f"  Keys: {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
            except Exception as e:
                print(f"Error {ep}: {e}")

if __name__ == "__main__":
    asyncio.run(probar_endpoints())
