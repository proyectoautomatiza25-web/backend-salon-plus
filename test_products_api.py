import asyncio
import os
import sys
import json
from dotenv import load_dotenv
import httpx

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.integrations.fudo_client import FudoClient

async def test_products():
    client = FudoClient()
    products = await client.fetch_products()
    print(f"Products fetched: {len(products)}")
    if products:
        print(f"Sample: {products[0]}")

if __name__ == "__main__":
    asyncio.run(test_products())
