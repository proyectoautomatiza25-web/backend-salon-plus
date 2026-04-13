import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.services.fudo_sync import FudoSyncService

async def test_sales_sync():
    print("--- 🛒 TESTING SALES SYNC ---")
    sales_result = await FudoSyncService.sync_sales(hours=72) # check last 3 days
    print(f"Sales Result: {sales_result}")

if __name__ == "__main__":
    asyncio.run(test_sales_sync())
