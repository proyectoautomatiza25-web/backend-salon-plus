"""
Imprime respuesta RAW de Ruka para entender qué devuelve.
"""
import asyncio, os
from dotenv import load_dotenv
import httpx

load_dotenv()

async def test_ruka_raw():
    headers = {
        "x-api-id": os.getenv("RUKA_API_ID"),
        "x-api-key": os.getenv("RUKA_API_KEY"),
    }
    url = "https://www.ruka.ai/api/v1/me"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        print(f"Body: {r.text[:500]}")

if __name__ == "__main__":
    asyncio.run(test_ruka_raw())
