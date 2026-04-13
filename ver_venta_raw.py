"""
Muestra la estructura completa de UNA venta de Fudo para mapear correctamente los campos.
"""
import asyncio, os, json
from dotenv import load_dotenv
import httpx
from datetime import date, timedelta

load_dotenv()

FUDO_BASE_URL = os.getenv("FUDO_BASE_URL", "https://api.fu.do").rstrip('/')
FUDO_BEARER_TOKEN = os.getenv("FUDO_BEARER_TOKEN", "")

async def ver_venta():
    headers = {
        "Authorization": f"Bearer {FUDO_BEARER_TOKEN}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "User-Agent": "Mozilla/5.0",
        "fudo-country-code": "CL"
    }
    hasta = date.today()
    desde = hasta - timedelta(days=3)

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{FUDO_BASE_URL}/sales",
            params={"from": desde.isoformat(), "to": hasta.isoformat()},
            headers=headers)
        
        if r.status_code == 200:
            data = r.json()
            # Tomar primera venta
            if isinstance(data, dict) and data:
                first_key = list(data.keys())[0]
                venta = data[first_key]
                print(f"=== ESTRUCTURA COMPLETA DE VENTA ID={first_key} ===")
                print(json.dumps(venta, indent=2, ensure_ascii=False, default=str))
                
                # Si hay 'order', mostrarlo también
                if 'order' in venta:
                    print(f"\n=== CAMPO 'order' ===")
                    print(json.dumps(venta['order'], indent=2, ensure_ascii=False, default=str))
            elif isinstance(data, list) and data:
                print("=== PRIMERA VENTA ===")
                print(json.dumps(data[0], indent=2, ensure_ascii=False, default=str))
        else:
            print(f"Error: {r.status_code} - {r.text[:300]}")

if __name__ == "__main__":
    asyncio.run(ver_venta())
