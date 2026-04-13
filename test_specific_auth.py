import asyncio
import os
import base64
import httpx
from dotenv import load_dotenv

async def test():
    base_url = "https://api.fu.do"
    
    # Try the one from debug_fudo.py
    print("\n--- Testing with credentials from debug_fudo.py ---")
    auth_str = "MzZAMTkxNDcz:Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {auth_b64}", "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{base_url}/products", headers=headers)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print("Success! These credentials work.")
                data = r.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"First product keys: {data[0].keys()}")
                    print(f"Sample product: {data[0]}")
            else:
                print(f"Error: {r.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test())
