import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://bcfulknkkwlpxpiuboyt.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

async def create_table():
    sql = """
    CREATE TABLE IF NOT EXISTS public.geofence_events (
        id SERIAL PRIMARY KEY,
        user_id TEXT,
        user_email TEXT,
        distance_meters INTEGER,
        bonus_crowns INTEGER,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        location TEXT
    );

    ALTER TABLE public.geofence_events ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS "service_role_all" ON public.geofence_events;
    CREATE POLICY "service_role_all" ON public.geofence_events FOR ALL USING (true);
    """
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Supabase doesn't have a direct SQL endpoint via REST usually, 
    # but we can try the /rest/v1/rpc or if it's not set up, 
    # we might have to tell the user to run it.
    # Actually, many people use n8n or similar.
    
    print("Please run the following SQL in your Supabase SQL Editor:")
    print(sql)

if __name__ == "__main__":
    asyncio.run(create_table())
