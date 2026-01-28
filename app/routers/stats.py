from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta
from .. import database, models, schemas, auth

router = APIRouter(prefix="/api", tags=["Stats"])

@router.get("/dashboard/resumen", response_model=schemas.DashboardStats)
def get_dashboard_summary(dias: int = 30, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    fecha_limite = datetime.utcnow() - timedelta(days=dias)
    
    # Base Stats
    query = db.query(models.Venta).filter(models.Venta.fecha >= fecha_limite)
    
    total_ventas = query.with_entities(func.sum(models.Venta.importe_total)).scalar() or 0
    cantidad_ventas = query.count()
    ticket_promedio = (total_ventas / cantidad_ventas) if cantidad_ventas > 0 else 0
    
    # Ventas por Canal
    canal_stats = query.with_entities(models.Venta.canal, func.sum(models.Venta.importe_total)).group_by(models.Venta.canal).all()
    ventas_por_canal = [{"canal": c, "total": float(t or 0)} for c, t in canal_stats]
    
    # Top Productos
    top_prods_q = db.query(
        models.ItemVenta.producto_nombre, 
        func.sum(models.ItemVenta.subtotal).label('total')
    ).join(models.Venta).filter(models.Venta.fecha >= fecha_limite).group_by(models.ItemVenta.producto_nombre).order_by(desc('total')).limit(5).all()
    top_productos = [{"nombre": n, "total": float(t)} for n, t in top_prods_q]

    # Top Clientes
    top_cli_q = db.query(
        models.Cliente.nombre,
        func.sum(models.Venta.importe_total).label('total')
    ).join(models.Venta).filter(models.Venta.fecha >= fecha_limite).group_by(models.Cliente.id).order_by(desc('total')).limit(5).all()
    top_clientes = [{"nombre": n, "total": float(t)} for n, t in top_cli_q]
    
    return {
        "ventas_total": float(total_ventas),
        "cantidad_ventas": cantidad_ventas,
        "ticket_promedio": float(ticket_promedio),
        "ventas_por_canal": ventas_por_canal,
        "top_productos": top_productos,
        "top_clientes": top_clientes
    }

@router.get("/productos/ranking", response_model=List[schemas.ProductoRanking])
def get_productos_ranking(top: int = 10, categoria: str = None, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.Producto)
    if categoria:
        query = query.filter(models.Producto.categoria == categoria)
    return query.order_by(models.Producto.ingresos_totales.desc()).limit(top).all()

@router.get("/clientes/top", response_model=List[schemas.ClienteResponse])
def get_clientes_top(top: int = 20, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Cliente).order_by(models.Cliente.gasto_total.desc()).limit(top).all()
