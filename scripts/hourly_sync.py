import asyncio
import httpx
import sys

# URL de tu backend desplegado
API_URL = "https://backend-salon-plus.vercel.app"

async def run_sync():
    print(f"🚀 Iniciando sincronización horaria: {API_URL}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Sincronizar Ventas (últimas 2 horas para seguridad)
        print("📦 Sincronizando ventas...")
        try:
            r_sales = await client.post(f"{API_URL}/api/fudo/sync-sales?hours=2")
            print(f"✅ Ventas: {r_sales.json()}")
        except Exception as e:
            print(f"❌ Error ventas: {e}")

        # 2. Sincronizar Menú
        print("☕ Sincronizando menú...")
        try:
            r_menu = await client.post(f"{API_URL}/api/fudo/sync-menu")
            print(f"✅ Menú: {r_menu.json()}")
        except Exception as e:
            print(f"❌ Error menú: {e}")

if __name__ == "__main__":
    asyncio.run(run_sync())
