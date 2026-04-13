import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://bcfulknkkwlpxpiuboyt.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

async def check_users():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/users?select=count", headers=headers)
        print(f"Total users in Supabase: {r.json()}")
        
        r = await client.get(f"{SUPABASE_URL}/rest/v1/geofence_events?select=count", headers=headers)
        print(f"Total geofence events in Supabase: {r.status_code} {r.text}")

if __name__ == "__main__":
    asyncio.run(check_users())
