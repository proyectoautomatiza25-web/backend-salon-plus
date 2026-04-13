import asyncio
from app.database import SessionLocal
from app.services.fudo_sync import sync_fudo_sales
from app.services.ruka_sync import sync_ruka_purchases
from datetime import date, timedelta

async def full_sync():
    print("🔄 Iniciando sincronización TOTAL (Fudo + Ruka)...")
    db = SessionLocal()
    try:
        # Últimos 30 días
        desde = date.today() - timedelta(days=30)
        hasta = date.today()
        
        print(f"📅 Rango: {desde} a {hasta}")
        
        # 1. Ventas (Fudo)
        ventas_count = await sync_fudo_sales(db, desde, hasta)
        print(f"✅ Fudo: {ventas_count} ventas nuevas sincronizadas.")
        
        # 2. Gastos (Ruka)
        gastos_count = await sync_ruka_purchases(db, desde, hasta)
        print(f"✅ Ruka: {gastos_count} compras nuevas sincronizadas.")
        
    finally:
        db.close()
    print("\n✨ ¡Sincronización completada!")

if __name__ == "__main__":
    asyncio.run(full_sync())
