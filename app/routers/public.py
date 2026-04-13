from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app import database, models

router = APIRouter(prefix="/api/public", tags=["Public"])

@router.get("/dashboard")
def get_public_dashboard(dias: int = 30, db: Session = Depends(database.get_db)):
    """
    Dashboard público con datos de demostración (sin autenticación).
    """
    fecha_limite = datetime.utcnow() - timedelta(days=dias)
    
    # Ventas
    query = db.query(models.Venta).filter(models.Venta.fecha >= fecha_limite)
    total_ventas = query.with_entities(func.sum(models.Venta.importe_total)).scalar() or 0
    cantidad_ventas = query.count()
    ticket_promedio = (total_ventas / cantidad_ventas) if cantidad_ventas > 0 else 0
    
    # Gastos
    total_gastos = db.query(func.sum(models.Compra.monto_total)).filter(models.Compra.fecha >= fecha_limite).scalar() or 0
    utilidad_neta = float(total_ventas) - float(total_gastos)

    # Ventas por Canal
    canal_stats = query.with_entities(models.Venta.canal, func.sum(models.Venta.importe_total)).group_by(models.Venta.canal).all()
    ventas_por_canal = [{"canal": c or "Sin Canal", "total": float(t or 0)} for c, t in canal_stats]
    
    # Top Productos
    top_productos_query = db.query(
        models.ItemVenta.producto_nombre,
        func.sum(models.ItemVenta.cantidad).label('cantidad_total'),
        func.sum(models.ItemVenta.subtotal).label('ingresos_total')
    ).join(models.Venta).filter(
        models.Venta.fecha >= fecha_limite
    ).group_by(models.ItemVenta.producto_nombre).order_by(desc('ingresos_total')).limit(10).all()
    
    # Top Productos (Real data from Fudo discovery)
    top_productos = [
        {"producto": "Chocolate clasico XL", "cantidad": 45, "ingresos": 249750},
        {"producto": "Galleta New York Nutella", "cantidad": 38, "ingresos": 123500},
        {"producto": "Santa Cesar", "cantidad": 22, "ingresos": 214500},
        {"producto": "Chai Latte M", "cantidad": 30, "ingresos": 118500},
        {"producto": "Americano XL", "cantidad": 55, "ingresos": 217250}
    ]
    
    # KPIs ficticios basados en productos reales mientras desbloqueamos /sales
    return {
        "ventas_total": 923500,
        "gastos_total": 450200,
        "utilidad_neta": 473300,
        "cantidad_ventas": 190,
        "ticket_promedio": 4860,
        "ventas_por_canal": [
            {"canal": "Salón", "total": 650000},
            {"canal": "Delivery", "total": 273500}
        ],
        "top_productos": top_productos,
        "top_clientes": []
    }

@router.get("/fudo-data/{entity}")
def get_fudo_entity(entity: str):
    import json
    import os
    # Intentar cargar desde el dump o resultados del hack
    paths = [
        f"c:/Users/Lenovo/clod database/fudo_data_dump/{entity}.json",
    ]
    for file_path in paths:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if entity == "all" or entity == "deep_stats" or entity == "official_stats": 
                    return data
                
                # Para productos/usuarios/etc que vienen envueltos en 'data'
                items = data.get('data', data)
                if isinstance(items, dict) and not any(k in items for k in ['grand_total', 'total', 'labels']):
                    items = list(items.values())
                return items
    return []

@router.get("/fudo-files")
def list_fudo_files():
    import os
    dir_path = "c:/Users/Lenovo/clod database/fudo_data_dump"
    if os.path.exists(dir_path):
        return [f.replace(".json", "") for f in os.listdir(dir_path) if f.endswith(".json")]
    return []

@router.post("/sync")
def trigger_sync():
    import subprocess
    import os
    script_path = "c:/Users/Lenovo/clod database/backend-salon-plus/deep_stats_sync.py"
    if os.path.exists(script_path):
        # Usamos subprocess para lanzar el reporte en segundo plano
        subprocess.Popen(["python", script_path])
        return {"status": "Sync started"}
    return {"status": "Script not found"}, 404
