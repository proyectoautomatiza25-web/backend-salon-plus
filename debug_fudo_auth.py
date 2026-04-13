import asyncio
import os
import base64
import httpx
from dotenv import load_dotenv

async def test():
    load_dotenv()
    client_id = os.getenv("FUDO_CLIENT_ID")
    client_secret = os.getenv("FUDO_CLIENT_SECRET")
    bearer_token = os.getenv("FUDO_BEARER_TOKEN")
    base_url = "https://api.fu.do"
    
    print(f"Testing with Client ID: {client_id}")
    
    # 1. Test with Bearer
    if bearer_token:
        print("\n--- Testing with Bearer Token ---")
        headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"{base_url}/products", headers=headers)
                print(f"Status: {r.status_code}")
                if r.status_code == 200:
                    print("Success! Bearer token works.")
                    # print(r.json()[:1])
                else:
                    print(f"Error: {r.text}")
            except Exception as e:
                print(f"Exception: {e}")

    # 2. Test with Basic Auth
    if client_id and client_secret:
        print("\n--- Testing with Basic Auth ---")
        token = f"{client_id}:{client_secret}"
        token_b64 = base64.b64encode(token.encode()).decode()
        headers = {"Authorization": f"Basic {token_b64}", "Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"{base_url}/products", headers=headers)
                print(f"Status: {r.status_code}")
                if r.status_code == 200:
                    print("Success! Basic Auth works.")
                else:
                    print(f"Error: {r.text}")
            except Exception as e:
                print(f"Exception: {e}")

    # 3. Test Refresh Token
    print("\n--- Testing Token Refresh ---")
    url = "https://auth.fu.do/api"
    payload = {"apiKey": client_id, "apiSecret": client_secret}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("Refresh successful!")
            print(f"New token: {r.json().get('token')[:20]}...")
        else:
            print(f"Refresh failed: {r.text}")

if __name__ == "__main__":
    asyncio.run(test())
