from sqlalchemy.orm import Session
from app.models import Compra, ItemCompra
from app.integrations.ruka_client import RukaClient
from datetime import date
from sqlalchemy import select

async def sync_ruka_purchases(db: Session, desde: date, hasta: date):
    """
    Extrae compras de Ruka y las guarda en la base de datos local.
    Evita duplicados usando el ruka_compra_id.
    """
    client = RukaClient()
    purchases_data = await client.fetch_purchases(desde, hasta)
    
    synced_count = 0
    for p_data in purchases_data:
        # 1. Verificar si ya existe (usando ID de ruka o Folio+Emisor si el ID es volátil)
        ruka_id = str(p_data.get("id"))
        existing = db.query(Compra).filter(Compra.ruka_compra_id == ruka_id).first()
        
        if not existing:
            # 2. Crear la Compra base
            nueva_compra = Compra(
                ruka_compra_id=ruka_id,
                fecha=p_data.get("fecha_emision"), # Ajustar según JSON real de Ruka
                proveedor_nombre=p_data.get("emisor_razon_social", "Proveedor Desconocido"),
                monto_total=p_data.get("monto_total", 0)
            )
            db.add(nueva_compra)
            db.flush() # Para obtener el ID de la nueva_compra
            
            # 3. Guardar items si vienen en el detalle
            items = p_data.get("detalles", [])
            for item in items:
                nuevo_item = ItemCompra(
                    compra_id=nueva_compra.id,
                    insumo_nombre=item.get("descripcion", "Sin nombre"),
                    cantidad=item.get("cantidad", 1),
                    costo_unitario=item.get("precio_unitario", 0),
                    subtotal=item.get("total", 0)
                )
                db.add(nuevo_item)
            
            synced_count += 1
    
    db.commit()
    return synced_count
