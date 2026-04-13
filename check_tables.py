import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    if not url or not key:
        print("Missing URL or KEY in .env")
        return
        
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{url}/rest/v1/", headers=headers)
        if r.status_code == 200:
            data = r.json()
            paths = list(data.get("paths", {}).keys())
            print("Paths found:", paths)
        else:
            print("Error:", r.status_code, r.text)

if __name__ == "__main__":
    asyncio.run(check())
