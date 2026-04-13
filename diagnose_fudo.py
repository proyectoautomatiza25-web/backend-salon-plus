"""
Script para diagnosticar el problema con la sincronización de Fudo en Vercel.
Prueba directamente el endpoint /sales/{id} con el sale 42946 mencionado por el usuario.
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

FUDO_BASE_URL = "https://api.fu.do/api"
FUDO_BEARER_TOKEN = os.getenv("FUDO_BEARER_TOKEN", "")
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "https://bcfulknkkwlpxpiuboyt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

async def test_sale_detail():
    """Prueba la estructura de la venta 42946 que el usuario mencionó."""
    headers = {
        "Authorization": f"Bearer {FUDO_BEARER_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "fudo-country-code": "CL"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        print("\n--- Test 1: Detalle de Venta ID 42946 ---")
        try:
            r = await client.get(f"{FUDO_BASE_URL}/sales/42946", headers=headers)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print("Keys:", list(data.keys()) if isinstance(data, dict) else type(data))
                # Mostrar campos clave
                if isinstance(data, dict):
                    print(f"  - id: {data.get('id')}")
                    print(f"  - total/importe: {data.get('total') or data.get('importe_total') or data.get('totalAmount')}")
                    print(f"  - client: {data.get('client') or data.get('cliente')}")
                    print(f"  - createdAt: {data.get('createdAt') or data.get('fecha')}")
                    print(f"  RAW (primeros 500 chars): {str(data)[:500]}")
            else:
                print("Error:", r.text[:200])
        except Exception as e:
            print(f"Exception: {e}")

        print("\n--- Test 2: Lista de ventas de hoy ---")
        from datetime import date, timedelta
        today = date.today()
        since = today - timedelta(days=3)
        try:
            r2 = await client.get(
                f"{FUDO_BASE_URL}/sales",
                params={"from": since.isoformat(), "to": today.isoformat()},
                headers=headers
            )
            print(f"Status: {r2.status_code}")
            if r2.status_code == 200:
                data2 = r2.json()
                print(f"Tipo respuesta: {type(data2)}")
                if isinstance(data2, dict):
                    print("Keys:", list(data2.keys()))
                    print("Total registros:", len(data2))
                elif isinstance(data2, list):
                    print("Total ventas:", len(data2))
                    if data2:
                        print("Primera venta keys:", list(data2[0].keys()) if isinstance(data2[0], dict) else data2[0])
            else:
                print("Error:", r2.text[:300])
        except Exception as e:
            print(f"Exception: {e}")

        print("\n--- Test 3: Ventas en Supabase ---")
        sb_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }
        try:
            r3 = await client.get(
                f"{SUPABASE_URL}/rest/v1/ventas_fudo",
                params={"select": "fudo_order_id,monto_total,cliente_telefono,puntos_generados,fecha_venta", "limit": "5", "order": "fecha_venta.desc"},
                headers=sb_headers
            )
            print(f"Supabase Status: {r3.status_code}")
            print(f"Supabase Records: {r3.text[:600]}")
        except Exception as e:
            print(f"Exception Supabase: {e}")

if __name__ == "__main__":
    asyncio.run(test_sale_detail())
