import asyncio
import os
from dotenv import load_dotenv
import httpx
from datetime import datetime, timedelta

# Cargar configuración
root_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(root_dir, ".env"))

async def test_sync_process():
    print("🚀 PROBADOR DE SCRAPING KINGDOM COFFEE")
    print("-" * 40)
    
    # 1. Verificar variables
    fudo_base = os.getenv("FUDO_BASE_URL")
    fudo_id = os.getenv("FUDO_CLIENT_ID")
    sb_url = os.getenv("VITE_SUPABASE_URL")
    
    print(f"Fudo Base: {fudo_base}")
    print(f"Fudo ID: {fudo_id[:5]}...")
    print(f"Supabase URL: {sb_url}")
    
    # 2. Probar conexión Fudo
    from app.integrations.fudo_client import FudoClient
    client = FudoClient()
    print("\n📦 Probando conexión con Fudo API...")
    res = await client.test_connection()
    print(f"Resultado Fudo: {res}")
    
    if not res.get("success"):
        print("❌ ERROR: No hay conexión con Fudo. Verifica FUDO_CLIENT_ID y SECRET.")
        return

    # 3. Probar sincronización de ventas (últimas 24h)
    from app.services.fudo_sync import FudoSyncService
    print("\n🛒 Probando Sincronización de Ventas (Scraping)...")
    sync_res = await FudoSyncService.sync_sales(hours=24)
    print(f"Resultado Sync: {sync_res}")
    
    if sync_res.get("success"):
        print(f"✅ ÉXITO: Se sincronizaron {sync_res.get('synced')} ventas correctamente.")
    else:
        print(f"❌ ERROR SYNC: {sync_res.get('message') or sync_res.get('error')}")
        print("\nTIP: Si dice 'relation ventas_fudo does not exist', ejecuta el SQL FINAL_REPAIR_v3.")

if __name__ == "__main__":
    asyncio.run(test_sync_process())
