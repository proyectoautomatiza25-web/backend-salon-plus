"""
Verificación de datos reales de Fudo:
- Muestra las ventas RAW que devuelve la API de Fudo
- Muestra lo que hay actualmente en Supabase
"""
import asyncio
import os
import json
from dotenv import load_dotenv
import httpx
from datetime import date, timedelta

load_dotenv()

FUDO_BASE_URL = os.getenv("FUDO_BASE_URL", "https://api.fu.do").rstrip('/')
FUDO_BEARER_TOKEN = os.getenv("FUDO_BEARER_TOKEN", "")
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

async def verificar():
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

    print(f"=== PASO 1: Datos RAW de Fudo ({desde} → {hasta}) ===")
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{FUDO_BASE_URL}/sales",
            params={"from": desde.isoformat(), "to": hasta.isoformat()},
            headers=headers
        )
        print(f"Status Fudo: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Tipo de respuesta: {type(data)}")
            
            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"Total ventas en dict: {len(keys)}")
                # Mostrar las primeras 3 ventas reales
                for i, (k, v) in enumerate(data.items()):
                    if i >= 3: break
                    print(f"\n  Venta ID={k}:")
                    if isinstance(v, dict):
                        print(f"    - total/amount: {v.get('total') or v.get('totalAmount') or v.get('importe_total')}")
                        print(f"    - fecha: {v.get('createdAt') or v.get('fecha') or v.get('created_at')}")
                        print(f"    - client: {v.get('client') or v.get('cliente')}")
                        print(f"    Keys disponibles: {list(v.keys())}")
                    else:
                        print(f"    Tipo: {type(v)}, Valor: {str(v)[:100]}")
            elif isinstance(data, list):
                print(f"Total ventas en lista: {len(data)}")
                for i, v in enumerate(data[:3]):
                    print(f"\n  Venta #{i+1}: {json.dumps(v, ensure_ascii=False)[:300]}")
            else:
                print("Respuesta inesperada:", str(data)[:300])
        else:
            print(f"Error Fudo: {r.text[:300]}")

    print("\n\n=== PASO 2: Lo que hay en Supabase actualmente ===")
    sb_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r2 = await client.get(
            f"{SUPABASE_URL}/rest/v1/ventas_fudo",
            params={
                "select": "fudo_order_id,monto_total,cliente_telefono,puntos_generados,fecha_venta",
                "order": "fecha_venta.desc",
                "limit": "10"
            },
            headers=sb_headers
        )
        print(f"Status Supabase: {r2.status_code}")
        if r2.status_code == 200:
            ventas = r2.json()
            print(f"Total en Supabase: {len(ventas)} registros (mostrando últimos 10):")
            for v in ventas:
                print(f"  ID={v.get('fudo_order_id')} | Monto=${v.get('monto_total')} | Tel={v.get('cliente_telefono')} | Pts={v.get('puntos_generados')} | Fecha={str(v.get('fecha_venta',''))[:10]}")
        else:
            print("Error Supabase:", r2.text[:300])

if __name__ == "__main__":
    asyncio.run(verificar())
