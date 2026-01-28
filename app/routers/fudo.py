from fastapi import APIRouter, HTTPException, Query
from datetime import date, datetime, timedelta
from typing import Optional

from app.integrations.fudo_client import FudoClient

router = APIRouter()


@router.get("/test-connection")
async def test_fudo_connection():
    """
    Prueba la conexión con la API de Fudo.
    
    Returns:
        dict: Estado de la conexión
    """
    try:
        client = FudoClient()
        result = await client.test_connection()
        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-orders")
async def test_fetch_orders(
    fecha_desde: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    """
    Endpoint de prueba para obtener órdenes de Fudo.
    
    Permite inspeccionar la estructura JSON que devuelve la API de Fudo
    para sus órdenes/ventas.
    
    Args:
        fecha_desde: Fecha de inicio (default: hace 7 días)
        fecha_hasta: Fecha de fin (default: hoy)
        
    Returns:
        dict: {"orders": [...]} con la respuesta cruda de Fudo
    """
    try:
        # Parsear fechas o usar defaults
        if fecha_desde:
            desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        else:
            desde = date.today() - timedelta(days=7)
            
        if fecha_hasta:
            hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
        else:
            hasta = date.today()
        
        # Validar rango
        if desde > hasta:
            raise HTTPException(
                status_code=400,
                detail="fecha_desde debe ser anterior a fecha_hasta"
            )
        
        # Obtener cliente y hacer petición
        client = FudoClient()
        orders = await client.fetch_orders(desde, hasta)
        
        return {
            "orders": orders
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format or config: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
async def fetch_fudo_products():
    """
    Obtiene el catálogo de productos de Fudo.
    
    Returns:
        dict: Lista de productos
    """
    try:
        client = FudoClient()
        products = await client.fetch_products()
        
        return {
            "success": True,
            "total_products": len(products),
            "products": products
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
