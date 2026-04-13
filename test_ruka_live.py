"""
Prueba conexión con Ruka AI.
"""
import asyncio, os
from dotenv import load_dotenv
import httpx
from datetime import date, timedelta

load_dotenv()

RUKA_API_ID = os.getenv("RUKA_API_ID")
RUKA_API_KEY = os.getenv("RUKA_API_KEY")

async def test_ruka():
    print(f"Testing Ruka with ID: {RUKA_API_ID}")
    headers = {
        "x-api-id": RUKA_API_ID,
        "x-api-key": RUKA_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Probamos varios endpoints posibles
    base_urls = [
        "https://www.ruka.ai/api/v1",
        "https://api.ruka.ai/v1",
        "https://ruka.ai/api/v1"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for base in base_urls:
            print(f"\nProbando Base URL: {base}")
            # Pruebas de endpoints
            for ep in ["/me", "/purchases", "/providers"]:
                url = f"{base}{ep}"
                try:
                    r = await client.get(url, headers=headers)
                    print(f"  Endpoint {ep}: {r.status_code}")
                    if r.status_code == 200:
                        print(f"  SUCCESS! Data: {str(r.json())[:200]}")
                except Exception as e:
                    print(f"  Error {ep}: {e}")

if __name__ == "__main__":
    asyncio.run(test_ruka())
