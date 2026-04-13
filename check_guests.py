
import asyncio
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from app.integrations.fudo_client import FudoClient

async def check_fudo_guests():
    load_dotenv()
    client = FudoClient()
    await client.refresh_token()
    
    hoy = date.today()
    desde = hoy - timedelta(days=30)
    
    print(f"Fetching sales from {desde}...")
    sales = await client.fetch_orders(desde, hoy)
    
    with_guest = [s for s in sales if isinstance(s, dict) and s.get("guestId")]
    
    print(f"Total sales in period: {len(sales)}")
    print(f"Sales with guestId: {len(with_guest)}")
    
    if with_guest:
        # Ver si el primer guest tiene teléfono
        gid = with_guest[0].get("guestId")
        headers = client.get_auth_headers()
        import httpx
        async with httpx.AsyncClient() as http_client:
            gr = await http_client.get(f"{client.base_url}/guests/{gid}", headers=headers)
            print(f"Guest {gid} status: {gr.status_code}")
            if gr.status_code == 200:
                print(f"Guest Data: {gr.json()}")

if __name__ == "__main__":
    asyncio.run(check_fudo_guests())
