import asyncio
import logging
from app.services.fudo_sync import FudoSyncService

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FudoSyncWorker")

async def run_sync_worker():
    """
    Sincronizador continuo de Fudo.
    Mantiene la base de datos local actualizada para que las consultas de los usuarios sean instantáneas.
    """
    logger.info("🚀 Iniciando Sync Worker de Fudo (High Frequency)...")
    
    while True:
        try:
            # 1. Sincronizar Ventas (Últimas 2 horas)
            logger.info("Sincronizando VENTAS recientes...")
            await FudoSyncService.sync_sales(hours=2)
            
            # 2. Sincronizar Facturas/Boletas (Últimos 2 días)
            logger.info("Sincronizando FACTURAS (Folios) recientes...")
            await FudoSyncService.sync_bills(days=2)
            
            logger.info("✅ Ciclo de sincronización completado. Esperando 5 minutos...")
            
        except Exception as e:
            logger.error(f"❌ Error en el ciclo de sincronización: {e}")
            
        # Esperar 5 minutos antes del próximo ciclo
        await asyncio.sleep(300)

if __name__ == "__main__":
    try:
        asyncio.run(run_sync_worker())
    except KeyboardInterrupt:
        logger.info("Sincronizador detenido por el usuario.")
