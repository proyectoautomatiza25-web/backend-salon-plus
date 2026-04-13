from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta
from .. import database, models, schemas, auth

router = APIRouter(prefix="/api", tags=["Stats"])

@router.get("/dashboard/resumen", response_model=schemas.DashboardStats)
def get_dashboard_summary(dias: int = 30, db: Session = Depends(database.get_db)):
    fecha_limite = datetime.utcnow() - timedelta(days=dias)
    
    # Base Stats (Ventas)
    query = db.query(models.Venta).filter(models.Venta.fecha >= fecha_limite)
    total_ventas = query.with_entities(func.sum(models.Venta.importe_total)).scalar() or 0
    cantidad_ventas = query.count()
    ticket_promedio = (total_ventas / cantidad_ventas) if cantidad_ventas > 0 else 0
    
    # Base Stats (Gastos desde Ruka/DB)
    total_gastos = db.query(func.sum(models.Compra.monto_total)).filter(models.Compra.fecha >= fecha_limite).scalar() or 0
    utilidad_neta = float(total_ventas) - float(total_gastos)

    # Ventas por Canal
    canal_stats = query.with_entities(models.Venta.canal, func.sum(models.Venta.importe_total)).group_by(models.Venta.canal).all()
    ventas_por_canal = [{"canal": c, "total": float(t or 0)} for c, t in canal_stats]
    
    # Top Productos
    top_productos_query = db.query(
        models.ItemVenta.producto_nombre,
        func.sum(models.ItemVenta.cantidad).label('cantidad_total'),
        func.sum(models.ItemVenta.subtotal).label('ingresos_total')
    ).join(models.Venta).filter(
        models.Venta.fecha >= fecha_limite
    ).group_by(models.ItemVenta.producto_nombre).order_by(desc('ingresos_total')).limit(10).all()
    
    top_productos = [{
        "producto": p[0],
        "cantidad": float(p[1] or 0),
        "ingresos": float(p[2] or 0)
    } for p in top_productos_query]
    
    # Top Clientes (si hay relación con cliente)
    top_clientes = []
    
    return {
        "ventas_total": float(total_ventas),
        "gastos_total": float(total_gastos),
        "utilidad_neta": utilidad_neta,
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
