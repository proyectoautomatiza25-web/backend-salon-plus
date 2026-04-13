import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def refresh():
    url = "https://auth.fu.do/api"
    apiKey = os.getenv("FUDO_CLIENT_ID")
    apiSecret = os.getenv("FUDO_CLIENT_SECRET")
    
    if not apiKey or not apiSecret:
        print("Missing Fudo credentials in .env")
        return
        
    payload = {"apiKey": apiKey, "apiSecret": apiSecret}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            token = r.json().get("token")
            print(f"NEW_TOKEN: {token}")
            
            # Updating .env file
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("FUDO_BEARER_TOKEN="):
                        f.write(f"FUDO_BEARER_TOKEN={token}\n")
                    else:
                        f.write(line)
            print("Successfully updated FUDO_BEARER_TOKEN in .env")
        else:
            print("Error refreshing token:", r.status_code, r.text)

if __name__ == "__main__":
    asyncio.run(refresh())
