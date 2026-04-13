from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional
from app.integrations.ruka_client import RukaClient
from app.database import get_db
from app.services.ruka_sync import sync_ruka_purchases

router = APIRouter()

@router.get("/test-connection")
async def test_ruka_connection():
    """Prueba la conexión con la API de Ruka."""
    try:
        client = RukaClient()
        result = await client.test_connection()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_purchases(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Sincroniza compras de Ruka a la DB local."""
    try:
        desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date() if fecha_desde else date.today() - timedelta(days=30)
        hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date() if fecha_hasta else date.today()
        
        count = await sync_ruka_purchases(db, desde, hasta)
        return {"success": True, "synced_count": count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-purchases")
async def test_fetch_purchases(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None)
):
    # ... (mantenemos el anterior para depurar)
    """Endpoint de prueba para extraer compras de Ruka."""
    try:
        if fecha_desde:
            desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        else:
            desde = date.today() - timedelta(days=30)
            
        if fecha_hasta:
            hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
        else:
            hasta = date.today()

        client = RukaClient()
        purchases = await client.fetch_purchases(desde, hasta)
        
        return {
            "success": True,
            "count": len(purchases),
            "purchases": purchases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
