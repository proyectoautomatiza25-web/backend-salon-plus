"""
Script para poblar la base de datos con compras de demostración de Ruka.
Esto permite visualizar el Dashboard con datos reales mientras se obtiene la URL correcta de la API.
"""
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Compra, ItemCompra
import random

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

def seed_demo_purchases():
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        existing = db.query(Compra).filter(Compra.ruka_compra_id.like("DEMO_%")).count()
        if existing > 0:
            print(f"⚠️ Ya existen {existing} compras de demostración. Limpiando...")
            db.query(ItemCompra).filter(ItemCompra.compra_id.in_(
                db.query(Compra.id).filter(Compra.ruka_compra_id.like("DEMO_%"))
            )).delete(synchronize_session=False)
            db.query(Compra).filter(Compra.ruka_compra_id.like("DEMO_%")).delete()
            db.commit()
        
        # Proveedores de ejemplo
        proveedores = [
            "Distribuidora Central Ltda.",
            "Comercial San Martín",
            "Importadora del Sur",
            "Proveedor Express Chile",
            "Mayorista Nacional"
        ]
        
        # Productos de ejemplo
        productos = [
            ("Café Premium 1kg", 8500, 12000),
            ("Leche Entera 1L", 950, 1200),
            ("Azúcar Refinada 1kg", 1200, 1500),
            ("Servilletas x100", 2500, 3000),
            ("Vasos Desechables x50", 3200, 4000),
            ("Papel Higiénico x12", 6500, 8000),
            ("Detergente 5L", 8900, 11000),
            ("Toallas de Papel x6", 5400, 6500),
            ("Bolsas Plásticas x100", 2800, 3500),
            ("Jabón Líquido 5L", 7200, 9000)
        ]
        
        # Generar 30 compras en los últimos 30 días
        compras_creadas = 0
        for i in range(30):
            fecha = datetime.now() - timedelta(days=random.randint(0, 30))
            proveedor = random.choice(proveedores)
            
            # Crear compra
            compra = Compra(
                ruka_compra_id=f"DEMO_COMPRA_{i+1:04d}",
                fecha=fecha,
                proveedor_nombre=proveedor,
                monto_total=Decimal("0")  # Se calculará después
            )
            db.add(compra)
            db.flush()
            
            # Agregar entre 2 y 6 items por compra
            num_items = random.randint(2, 6)
            total_compra = Decimal("0")
            
            for _ in range(num_items):
                producto_nombre, costo_min, costo_max = random.choice(productos)
                cantidad = random.randint(1, 10)
                costo_unitario = Decimal(str(random.randint(costo_min, costo_max)))
                subtotal = costo_unitario * cantidad
                
                item = ItemCompra(
                    compra_id=compra.id,
                    insumo_nombre=producto_nombre,
                    cantidad=Decimal(str(cantidad)),
                    costo_unitario=costo_unitario,
                    subtotal=subtotal
                )
                db.add(item)
                total_compra += subtotal
            
            # Actualizar total de la compra
            compra.monto_total = total_compra
            compras_creadas += 1
        
        db.commit()
        print(f"✅ Se crearon {compras_creadas} compras de demostración exitosamente")
        print(f"💰 Total gastado (demo): ${sum([c.monto_total for c in db.query(Compra).filter(Compra.ruka_compra_id.like('DEMO_%')).all()]):,.0f} CLP")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Poblando base de datos con compras de demostración...")
    seed_demo_purchases()
