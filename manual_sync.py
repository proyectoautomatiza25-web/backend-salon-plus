
import asyncio
import os
import json
from dotenv import load_dotenv
from app.services.fudo_sync import FudoSyncService

async def run_manual_sync():
    load_dotenv()
    print("🚀 Iniciando sincronización manual de ventas (última semana)...")
    result = await FudoSyncService.sync_sales(hours=168)
    print(f"Resultado: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(run_manual_sync())
