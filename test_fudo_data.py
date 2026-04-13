import asyncio
import os
from dotenv import load_dotenv
from app.integrations.fudo_client import FudoClient

async def test():
    load_dotenv()
    client = FudoClient()
    
    print("Testing connection...")
    conn = await client.test_connection()
    print(f"Connection result: {conn}")
    
    if conn['success']:
        print("Fetching categories...")
        cats = await client.fetch_categories()
        print(f"Found {len(cats)} categories")
        if cats:
            print(f"First category: {cats[0]}")
            
        print("Fetching products...")
        prods = await client.fetch_products()
        print(f"Found {len(prods)} products")
        if prods:
            print(f"First product sample: {prods[0]}")
    else:
        print("Failed to connect to Fudo")

if __name__ == "__main__":
    asyncio.run(test())
