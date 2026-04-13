import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def get_schema():
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{url}/rest/v1/", headers=headers)
        if r.status_code == 200:
            data = r.json()
            defs = data.get("definitions", {})
            ventas = defs.get("ventas_fudo", {})
            print("ventas_fudo columns:")
            for col, props in ventas.get("properties", {}).items():
                print(f"- {col}: {props.get('type')}")
        else:
            print(f"Error: {r.status_code} {r.text}")

if __name__ == "__main__":
    asyncio.run(get_schema())
