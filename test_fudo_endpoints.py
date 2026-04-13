import asyncio
import os
import sys
import json
from dotenv import load_dotenv
import httpx

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.integrations.fudo_client import FudoClient
from datetime import date, timedelta

async def test_api_direct():
    client = FudoClient()
    headers = client.get_auth_headers()
    
    hasta = date.today()
    desde = date.today() - timedelta(days=30)
    
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        # TEST 1: /v1/sales (API Oficial)
        try:
            r = await http_client.get(f"{client.base_url}/v1/sales", headers=headers, params={"from": desde.isoformat(), "to": hasta.isoformat()})
            results["v1_sales"] = {"status": r.status_code, "text": r.text[:500]}
        except Exception as e:
            results["v1_sales"] = {"error": str(e)}

        # TEST 2: /sales
        try:
            r = await http_client.get(f"{client.base_url}/sales", headers=headers, params={"from": desde.isoformat(), "to": hasta.isoformat()})
            results["sales"] = {"status": r.status_code, "text": r.text[:500]}
        except Exception as e:
            results["sales"] = {"error": str(e)}
            
    with open("fudo_api_test.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(test_api_direct())
