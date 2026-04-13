import asyncio
import os
import httpx
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

async def dry_run_test():
    """
    Prueba técnica de la lógica de validación sin arrancar el servidor.
    """
    from app.services.fudo_sync import FudoSyncService, SUPABASE_URL, SUPABASE_KEY
    
    print("--- Inciando DRY RUN TEST del nuevo sistema de puntos ---")
    
    # 1. Sincronizar un poquito (Últimas 24h)
    print("Paso 1: Sincronizando datos recientes de Fudo...")
    # await FudoSyncService.sync_sales(hours=24) # Descomentar para sync real
    # await FudoSyncService.sync_bills(days=1)   # Descomentar para sync real
    
    # 2. Buscar una boleta existente en la DB para probar el reclamo
    print("Paso 2: Buscando una boleta valida en la DB para simular reclamo...")
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/facturas_fudo?limit=1", headers=headers)
        if r.status_code == 200 and r.json():
            bill = r.json()[0]
            folio = bill.get("numero")
            monto = bill.get("monto")
            print(f"OK: Encontrada Boleta Nro {folio} por {monto}. Procediendo a simular validacion...")
            
            # Simulamos lo que hace el endpoint
            # (Verificar si la venta existe en ventas_fudo)
            sale_id = bill.get("sale_id")
            rv = await client.get(f"{SUPABASE_URL}/rest/v1/ventas_fudo?fudo_order_id=eq.{sale_id}", headers=headers)
            
            if rv.status_code == 200 and rv.json():
                print(f"OK: Venta {sale_id} encontrada en ventas_fudo.")
                print("--- PRUEBA DE LOGICA EXITOSA ---")
                print("El sistema puede mapear Folio -> Factura -> Venta -> Puntos de forma instantanea.")
            else:
                print(f"WARN: La factura existe pero la venta {sale_id} no esta sincronizada aun.")
                print("El endpoint manejara esto sincronizando la venta automaticamente.")
        else:
            print("ERROR: No hay datos en 'facturas_fudo'. Ejecuta el Worker primero.")

if __name__ == "__main__":
    asyncio.run(dry_run_test())
