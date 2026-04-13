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
    
    base_url = "https://api.fu.do/products"
    
    combos = [
        ("Bearer", {"Authorization": f"Bearer {bearer}"}),
        ("Basic Raw", {"Authorization": "Basic " + base64.b64encode(f"{cid}:{csec}".encode()).decode()}),
        ("Basic Decoded", {"Authorization": "Basic " + base64.b64encode(f"{base64.b64decode(cid).decode()}:{csec}".encode()).decode()}),
        ("Basic CID as Password", {"Authorization": "Basic " + base64.b64encode(f"{cid}:{csec}".encode()).decode()}),
        ("Token as Password", {"Authorization": "Basic " + base64.b64encode(f"token:{csec}".encode()).decode()}),
        ("Old Key", {"Authorization": "Basic " + base64.b64encode("36@191473:Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC".encode()).decode()})
    ]
    
    async with httpx.AsyncClient() as client:
        for name, headers in combos:
            headers["Accept"] = "application/json"
            try:
                r = await client.get(base_url, headers=headers)
                print(f"{name}: {r.status_code}")
            except Exception as e:
                print(f"{name}: Exception {e}")

if __name__ == "__main__":
    asyncio.run(test_combos())
