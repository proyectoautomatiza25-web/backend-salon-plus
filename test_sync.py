import asyncio
from app.services.fudo_sync import FudoSyncService

async def run():
    res = await FudoSyncService.sync_sales(24)
    print(res)

if __name__ == "__main__":
    asyncio.run(run())
