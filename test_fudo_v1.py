import asyncio
import base64
import httpx
import os
from dotenv import load_dotenv

async def test_combos():
    load_dotenv()
    cid = "MDAwMDA1OjE5MTQ3Mw=="
    csec = "0PVD917ZtoZiDopOfVmwW2oq"
    bearer = "eyJhbGciOiJIUzI1NiJ9.eyJhaSI6MTkxNDczLCJ1aSI6MzYsImV4cCI6MTc3MDg2Njg0MX0.QtDb4t3v5SLP9jXTEGOJegSBhegc7a34dya_VgPDdek"
    
    # Try with /v1
    base_url = "https://api.fu.do/v1/products"
    
    combos = [
        ("Bearer v1", {"Authorization": f"Bearer {bearer}"}),
        ("Basic Decoded v1", {"Authorization": "Basic " + base64.b64encode(f"{base64.b64decode(cid).decode()}:{csec}".encode()).decode()}),
        ("Bearer root", {"Authorization": f"Bearer {bearer}"}, "https://api.fu.do/products"),
    ]
    
    async with httpx.AsyncClient() as client:
        for name, headers, *url in combos:
            u = url[0] if url else base_url
            headers["Accept"] = "application/json"
            try:
                r = await client.get(u, headers=headers)
                print(f"{name}: {r.status_code}")
                if r.status_code == 200:
                    print(f"  FOUND DATA on {name}")
            except Exception as e:
                print(f"{name}: Exception {e}")

if __name__ == "__main__":
    asyncio.run(test_combos())
