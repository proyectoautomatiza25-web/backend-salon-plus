from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io
from .. import database, models, schemas, auth

router = APIRouter(prefix="/api/ventas", tags=["Ventas"])

@router.get("/", response_model=List[schemas.VentaResponse])
def get_ventas(
    page: int = 1,
    page_size: int = 20,
    canal: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Venta)
    
    if canal:
        query = query.filter(models.Venta.canal == canal)
    if fecha_desde:
        query = query.filter(models.Venta.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.Venta.fecha <= fecha_hasta)
        
    query = query.order_by(models.Venta.fecha.desc())
    
    ventas = query.offset((page - 1) * page_size).limit(page_size).all()
    return ventas

@router.get("/{venta_id}", response_model=schemas.VentaResponse)
def get_venta(venta_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    venta = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@router.post("/upload-csv", status_code=201)
async def upload_csv_ventas(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Sube un archivo Excel (.xlsx) o CSV exportado de Fudo para importar ventas masivamente.
    """
    
    # 1. Leer archivo
    contents = await file.read()
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents))
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use .xlsx o .csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo archivo: {str(e)}")

    # 2. Normalizar nombres de columnas (limpieza básica)
    # Fudo suele tener columnas como: "Fecha", "Mesa", "Camarero", "Cliente", "Total", "Estado", "Productos"
    df.columns = [c.strip().lower() for c in df.columns]
    
    count_created = 0
    errors = []

    # 3. Iterar y guardar
    # Nota: Los reportes de ventas suelen tener 1 fila por venta, o 1 fila por producto
    # Asumiremos formato "Detallado" (1 fila por producto) o "Resumido" (1 fila por venta)
    # Para simplificar este MVP, intentaremos detectar el formato.
    
    # Si tiene columna "producto" o "item", es detallado.
    is_detailed = 'producto' in df.columns or 'item' in df.columns
    
    # Agrupar si es detallado
    if is_detailed:
        # Necesitamos un ID de grupo, usaremos 'ticket' o 'id' o crearemos uno basado en fecha+mesa+total
        group_col = next((c for c in ['nro', 'ticket', '#', 'id'] if c in df.columns), None)
        if group_col:
            grouped = df.groupby(group_col)
        else:
            # Fallback peligroso: no agrupar, considerar cada fila una venta (probablemente mal)
            # Mejor tratamos de inferir
            pass

    # APROXIMACIÓN SEGURA MVP: 
    # Si Fudo exporta "Ventas" (1 fila por ticket), usaremos eso.
    # Buscamos columnas clave
    
    for index, row in df.iterrows():
        try:
            # Mapeo de columnas (Ajustar según reporte real de Fudo)
            # Intentamos ser flexibles con nombres comunes
            fecha_val = row.get('fecha') or row.get('date') or datetime.now()
            if isinstance(fecha_val, str):
                try:
                    fecha_dt = pd.to_datetime(fecha_val).to_pydatetime()
                except:
                    fecha_dt = datetime.now()
            else:
                 fecha_dt = fecha_val

            ticket_id = str(row.get('nro') or row.get('ticket') or row.get('#') or f"IMP-{index}")
            total = float(str(row.get('total') or row.get('monto') or 0).replace('$','').replace('.','').replace(',','.'))
            
            # Verificar duplicado
            existing = db.query(models.Venta).filter(models.Venta.fudo_ticket_id == ticket_id).first()
            if existing:
                continue

            # Cliente
            cliente_nombre = str(row.get('cliente') or "Cliente Casual")
            cliente_db = None
            if cliente_nombre and cliente_nombre != "nan":
                 cliente_db = db.query(models.Cliente).filter(models.Cliente.nombre == cliente_nombre).first()
                 if not cliente_db:
                     cliente_db = models.Cliente(nombre=cliente_nombre, gasto_total=0, pedidos_totales=0)
                     db.add(cliente_db)
                     db.flush()
            
            # Crear Venta
            venta = models.Venta(
                fudo_ticket_id=ticket_id,
                fecha=fecha_dt,
                canal=str(row.get('canal') or 'Importado'),
                metodo_pago=str(row.get('forma de pago') or row.get('medio de pago') or 'Efectivo'),
                mesa=str(row.get('mesa') or ''),
                mesero=str(row.get('camarero') or row.get('mesero') or ''),
                estado='cerrada',
                importe_total=total,
                cliente_id=cliente_db.id if cliente_db else None
            )
            db.add(venta)
            
            # Actualizar cliente stats
            if cliente_db:
                cliente_db.pedidos_totales += 1
                cliente_db.gasto_total += total
                if not cliente_db.ultima_compra or fecha_dt > cliente_db.ultima_compra:
                    cliente_db.ultima_compra = fecha_dt

            # Items (Si el excel no tiene items, no creamos items, solo la venta financiera)
            # Si quisieramos items, necesitariamos el reporte detallado
            
            count_created += 1

        except Exception as e:
            errors.append(f"Fila {index}: {str(e)}")
            continue

    db.commit()
    
    return {
        "message": "Importación finalizada",
        "created": count_created,
        "errors_count": len(errors),
        "first_5_errors": errors[:5]
    }

@router.post("/importar", status_code=201)
def importar_ventas(
    ventas_data: List[schemas.VentaImport],
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(auth.get_current_user) # Optional: remove auth for external webhook ease or keep it
):
    """
    Endpoint para recibir Webhooks o Importaciones Masivas de Fudo (JSON structurado).
    """
    count_created = 0
    count_updated = 0
    
    for v_in in ventas_data:
        # 1. Check or Create Cliente
        cliente_db = None
        if v_in.cliente and v_in.cliente.fudo_cliente_id:
            cliente_db = db.query(models.Cliente).filter(models.Cliente.fudo_cliente_id == v_in.cliente.fudo_cliente_id).first()
            if not cliente_db:
                cliente_db = models.Cliente(
                    fudo_cliente_id=v_in.cliente.fudo_cliente_id,
                    nombre=v_in.cliente.nombre,
                    telefono=v_in.cliente.telefono,
                    email=v_in.cliente.email,
                    ultima_compra=v_in.fecha
                )
                db.add(cliente_db)
                db.flush() # get ID
            else:
                # Update cliente stats logic usually goes here or is recalculated
                cliente_db.ultima_compra = max(cliente_db.ultima_compra, v_in.fecha) if cliente_db.ultima_compra else v_in.fecha
                
        # 2. Check Exists Venta
        existing_venta = db.query(models.Venta).filter(models.Venta.fudo_ticket_id == v_in.fudo_ticket_id).first()
        if existing_venta:
            # Update status if changed? For now, we skip or simple update
            count_updated += 1
            continue

        # 3. Create Venta
        new_venta = models.Venta(
            fudo_ticket_id=v_in.fudo_ticket_id,
            fecha=v_in.fecha,
            canal=v_in.canal,
            metodo_pago=v_in.metodo_pago,
            mesero=v_in.mesero,
            caja=v_in.caja,
            mesa=v_in.mesa,
            importe_total=v_in.importe_total,
            estado=v_in.estado,
            cliente_id=cliente_db.id if cliente_db else None
        )
        db.add(new_venta)
        db.flush()
        
        # 4. Create Items & Update Products
        for item_in in v_in.items:
            # Check Product (Upsert by Name for now, ideally by ID)
            prod = db.query(models.Producto).filter(models.Producto.nombre == item_in.producto_nombre).first()
            if not prod:
                prod = models.Producto(
                    nombre=item_in.producto_nombre,
                    categoria=item_in.categoria,
                    ventas_totales=0,
                    ingresos_totales=0
                )
                db.add(prod)
                db.flush()
            
            # Update Prod Stats
            prod.ventas_totales += item_in.cantidad
            prod.ingresos_totales += item_in.subtotal
            prod.ultima_actualizacion = datetime.utcnow()

            # Create ItemVenta
            new_item = models.ItemVenta(
                venta_id=new_venta.id,
                producto_id=prod.id,
                producto_nombre=item_in.producto_nombre,
                categoria=item_in.categoria,
                cantidad=item_in.cantidad,
                precio_unitario=item_in.precio_unitario,
                subtotal=item_in.subtotal
            )
            db.add(new_item)
        
        # Update Client Stats
        if cliente_db:
            cliente_db.pedidos_totales += 1
            cliente_db.gasto_total += v_in.importe_total

        count_created += 1

    db.commit()
    return {"message": f"Procesado. Creados: {count_created}, Actualizados/Saltados: {count_updated}"}
