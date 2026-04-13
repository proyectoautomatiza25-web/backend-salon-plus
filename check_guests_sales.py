"""
Busca ventas con guestId en el último mes para verificar la lógica de WhatsApp.
"""
import asyncio, os, json
from dotenv import load_dotenv
import httpx
from datetime import date, timedelta

load_dotenv()
FUDO_BASE_URL = os.getenv("FUDO_BASE_URL", "https://api.fu.do").rstrip('/')
FUDO_BEARER_TOKEN = os.getenv("FUDO_BEARER_TOKEN", "")

async def buscar_ventas_con_cliente():
    headers = {
        "Authorization": f"Bearer {FUDO_BEARER_TOKEN}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "User-Agent": "Mozilla/5.0",
        "fudo-country-code": "CL"
    }
    hasta = date.today()
    desde = hasta - timedelta(days=30)

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{FUDO_BASE_URL}/sales",
            params={"from": desde.isoformat(), "to": hasta.isoformat()},
            headers=headers)

        if r.status_code == 200:
            data = r.json()
            ventas = list(data.values()) if isinstance(data, dict) else data
            ventas_con_cliente = [v for v in ventas if v.get('guestId')]
            
            print(f"Total ventas en el mes: {len(ventas)}")
            print(f"Ventas con guestId: {len(ventas_con_cliente)}")
            
            if ventas_con_cliente:
                for v in ventas_con_cliente[:5]:
                    print(f"\nVenta ID={v.get('id')} | guestId={v.get('guestId')}")
                    # Consultar el guest
                    rg = await client.get(f"{FUDO_BASE_URL}/guests/{v.get('guestId')}", headers=headers)
                    if rg.status_code == 200:
                        guest = rg.json()
                        print(f"  Nombre: {guest.get('name')}")
                        print(f"  Phone: {guest.get('phone')}")
                    else:
                        print(f"  Error consultando guest: {rg.status_code}")
            else:
                print("No se encontraron ventas con cliente asociado en el último mes.")
        else:
            print(f"Error Fudo: {r.status_code}")

if __name__ == "__main__":
    asyncio.run(buscar_ventas_con_cliente())
