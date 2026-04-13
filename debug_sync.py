import asyncio
import os
import json
from dotenv import load_dotenv
from app.services.fudo_sync import FudoSyncService

async def main():
    load_dotenv()
    print("🚀 Iniciando prueba de sincronización...")
    res = await FudoSyncService.sync_sales(hours=24)
    print(f"📊 Resultado: {json.dumps(res, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
