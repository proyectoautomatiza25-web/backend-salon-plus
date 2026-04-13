import asyncio
import os
import sys
from dotenv import load_dotenv
import httpx

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.integrations.fudo_client import FudoClient
from datetime import date, timedelta

async def test_api_direct():
    client = FudoClient()
    headers = client.get_auth_headers()
    print(f"Headers: {headers}")
    
    hasta = date.today()
    desde = date.today() - timedelta(days=30)
    
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        # TEST 1
        print("\n--- TEST /sales ---")
        try:
            r = await http_client.get(f"{client.base_url}/sales", headers=headers, params={"from": desde.isoformat(), "to": hasta.isoformat()})
            print(f"Status: {r.status_code}")
            print(f"Text: {r.text[:500]}")
        except Exception as e:
            print(e)
            
        # TEST 2
        print("\n--- TEST /sale_identifiers ---")
        try:
            r = await http_client.get(f"{client.base_url}/sale_identifiers", headers=headers)
            print(f"Status: {r.status_code}")
            print(f"Text: {r.text[:500]}")
        except Exception as e:
            print(e)
            
        # TEST 3
        print("\n--- TEST /v2/sales ---")
        try:
            r = await http_client.get(f"{client.base_url}/v2/sales", headers=headers, params={"from": desde.isoformat(), "to": hasta.isoformat()})
            print(f"Status: {r.status_code}")
            print(f"Text: {r.text[:500]}")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    asyncio.run(test_api_direct())
