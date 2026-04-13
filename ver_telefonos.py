"""
Inspecciona los mobileToken reales de Fudo para entender el formato de los teléfonos.
"""
import asyncio, os
from dotenv import load_dotenv
import httpx
from datetime import date, timedelta

load_dotenv()
FUDO_BASE_URL = os.getenv("FUDO_BASE_URL", "https://api.fu.do").rstrip('/')
FUDO_BEARER_TOKEN = os.getenv("FUDO_BEARER_TOKEN", "")

async def ver_telefonos():
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

        if r.status_code == 200:
            data = r.json()
            ventas = list(data.values()) if isinstance(data, dict) else data
            print(f"Total ventas: {len(ventas)}\n")
            print(f"{'ID':<8} {'mobileToken':<20} {'Normalizado WhatsApp':<20} {'Total'}")
            print("-" * 70)
            for v in ventas:
                token = v.get('mobileToken') or ""
                digits = "".join(filter(str.isdigit, str(token)))
                
                # Normalizacion para WhatsApp formato chileno
                if digits.startswith("569") and len(digits) == 11:
                    wa = digits  # ya correcto: 56912345678
                elif digits.startswith("9") and len(digits) == 9:
                    wa = "56" + digits  # 569XXXXXXXX
                elif digits.startswith("56") and len(digits) == 11:
                    wa = digits  # ya tiene código
                elif len(digits) == 8:
                    wa = "569" + digits  # sin 9 inicial
                elif digits:
                    wa = digits  # desconocido, dejar como está
                else:
                    wa = None
                
                additions = v.get('additions') or []
                total = sum(float(a.get('price',0)) * float(a.get('count',1)) for a in additions
                           if not a.get('cancellationComment'))
                if not total:
                    total = sum(float(p.get('amount',0)) for p in (v.get('payments') or []) if not p.get('canceled'))
                
                print(f"{v.get('id'):<8} {token:<20} {wa or 'N/A':<20} ${total:,.0f}")
        else:
            print(f"Error: {r.status_code}")

if __name__ == "__main__":
    asyncio.run(ver_telefonos())
