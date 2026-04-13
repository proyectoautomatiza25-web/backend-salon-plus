"""
Busca todos los campos posibles que tengan info del cliente en una venta de Fudo.
"""
import asyncio, os, json
from dotenv import load_dotenv
import httpx
from datetime import date, timedelta

load_dotenv()
FUDO_BASE_URL = os.getenv("FUDO_BASE_URL", "https://api.fu.do").rstrip('/')
FUDO_BEARER_TOKEN = os.getenv("FUDO_BEARER_TOKEN", "")

async def buscar_cliente():
    headers = {
        "Authorization": f"Bearer {FUDO_BEARER_TOKEN}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "User-Agent": "Mozilla/5.0",
        "fudo-country-code": "CL"
    }
    hasta = date.today()
    desde = hasta - timedelta(days=7)

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{FUDO_BASE_URL}/sales",
            params={"from": desde.isoformat(), "to": hasta.isoformat()},
            headers=headers)

        data = r.json()
        ventas = list(data.values()) if isinstance(data, dict) else data
        
        # Tomar una venta que tenga monto > 0
        for v in ventas:
            additions = v.get('additions') or []
            total = sum(float(a.get('price',0)) * float(a.get('count',1)) for a in additions if not a.get('cancellationComment'))
            if total > 0:
                print(f"=== Venta ID={v.get('id')} - Total ${total:,.0f} ===")
                print("TODOS LOS CAMPOS DE NIVEL RAÍZ:")
                for k, val in v.items():
                    if k != 'additions':
                        print(f"  {k}: {json.dumps(val, ensure_ascii=False, default=str)[:150]}")
                print()
                
                # Buscar en guestId usando endpoint de guests
                guest_id = v.get('guestId')
                print(f"  guestId: {guest_id}")
                
                # Ver deliveryData
                dd = v.get('deliveryData') or {}
                print(f"  deliveryData completo: {json.dumps(dd, ensure_ascii=False)}")
                break
        
        # También intentar buscar el endpoint de guests/clientes
        print("\n=== Probando endpoint /guests ===")
        rg = await client.get(f"{FUDO_BASE_URL}/guests", headers=headers, 
                              params={"limit": 5})
        print(f"Status /guests: {rg.status_code}")
        if rg.status_code == 200:
            gdata = rg.json()
            print("Primeros guests:")
            guests = list(gdata.values())[:3] if isinstance(gdata, dict) else gdata[:3]
            for g in guests:
                print(json.dumps(g, indent=2, ensure_ascii=False, default=str)[:400])
        else:
            print(rg.text[:200])

if __name__ == "__main__":
    asyncio.run(buscar_cliente())
