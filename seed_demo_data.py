"""
Script para poblar la base de datos con datos de demostración realistas.
Simula ventas de Fudo y compras de Ruka para visualizar el Dashboard.
"""
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Venta, ItemVenta, Compra, ItemCompra
import random

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

def seed_demo_sales():
    """Crea ventas de demostración (simulando datos de Fudo)"""
    db = SessionLocal()
    
    try:
        # Limpiar datos demo anteriores
        db.query(ItemVenta).filter(ItemVenta.venta_id.in_(
            db.query(Venta.id).filter(Venta.fudo_ticket_id.like("DEMO_%"))
        )).delete(synchronize_session=False)
        db.query(Venta).filter(Venta.fudo_ticket_id.like("DEMO_%")).delete()
        db.commit()
        
        productos = [
            ("Café Americano", 2500, 3500),
            ("Café Latte", 3000, 4000),
            ("Cappuccino", 3200, 4200),
            ("Sandwich Pollo", 4500, 6000),
            ("Ensalada César", 5500, 7000),
            ("Jugo Natural", 2800, 3500),
            ("Torta Chocolate", 3500, 4500),
            ("Croissant", 2000, 2800),
        ]
        
        canales = ["PRESENCIAL", "DELIVERY", "RAPPI", "UBER_EATS"]
        
        ventas_creadas = 0
        total_vendido = Decimal("0")
        
        # Generar 50 ventas en los últimos 30 días
        for i in range(50):
            fecha = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(8, 22))
            canal = random.choice(canales)
            
            venta = Venta(
                fudo_ticket_id=f"DEMO_VENTA_{i+1:04d}",
                fecha=fecha,
                canal=canal,
                importe_total=Decimal("0"),
                estado="cerrada"
            )
            db.add(venta)
            db.flush()
            
            # Agregar entre 1 y 4 items por venta
            num_items = random.randint(1, 4)
            total_venta = Decimal("0")
            
            for _ in range(num_items):
                producto_nombre, precio_min, precio_max = random.choice(productos)
                cantidad = random.randint(1, 3)
                precio_unitario = Decimal(str(random.randint(precio_min, precio_max)))
                subtotal = precio_unitario * cantidad
                
                item = ItemVenta(
                    venta_id=venta.id,
                    producto_nombre=producto_nombre,
                    cantidad=Decimal(str(cantidad)),
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
                db.add(item)
                total_venta += subtotal
            
            venta.importe_total = total_venta
            total_vendido += total_venta
            ventas_creadas += 1
        
        db.commit()
        print(f"✅ Creadas {ventas_creadas} ventas de demostración")
        print(f"💰 Total vendido (demo): ${total_vendido:,.0f} CLP")
        return ventas_creadas, float(total_vendido)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

def seed_demo_purchases():
    """Crea compras de demostración (simulando datos de Ruka)"""
    db = SessionLocal()
    
    try:
        # Limpiar datos demo anteriores
        db.query(ItemCompra).filter(ItemCompra.compra_id.in_(
            db.query(Compra.id).filter(Compra.ruka_compra_id.like("DEMO_%"))
        )).delete(synchronize_session=False)
        db.query(Compra).filter(Compra.ruka_compra_id.like("DEMO_%")).delete()
        db.commit()
        
        proveedores = [
            "Distribuidora Central Ltda.",
            "Comercial San Martín",
            "Importadora del Sur",
            "Proveedor Express Chile",
        ]
        
        insumos = [
            ("Café Premium 1kg", 8500, 12000),
            ("Leche Entera 1L", 950, 1200),
            ("Azúcar Refinada 1kg", 1200, 1500),
            ("Servilletas x100", 2500, 3000),
            ("Vasos Desechables x50", 3200, 4000),
            ("Pan Hallulla x20", 4500, 5500),
            ("Queso Mantecoso 1kg", 7500, 9000),
            ("Jamón 1kg", 8900, 11000),
        ]
        
        compras_creadas = 0
        total_gastado = Decimal("0")
        
        # Generar 20 compras en los últimos 30 días
        for i in range(20):
            fecha = datetime.now() - timedelta(days=random.randint(0, 30))
            proveedor = random.choice(proveedores)
            
            compra = Compra(
                ruka_compra_id=f"DEMO_COMPRA_{i+1:04d}",
                fecha=fecha,
                proveedor_nombre=proveedor,
                monto_total=Decimal("0")
            )
            db.add(compra)
            db.flush()
            
            # Agregar entre 3 y 6 items por compra
            num_items = random.randint(3, 6)
            total_compra = Decimal("0")
            
            for _ in range(num_items):
                insumo_nombre, costo_min, costo_max = random.choice(insumos)
                cantidad = random.randint(2, 15)
                costo_unitario = Decimal(str(random.randint(costo_min, costo_max)))
                subtotal = costo_unitario * cantidad
                
                item = ItemCompra(
                    compra_id=compra.id,
                    insumo_nombre=insumo_nombre,
                    cantidad=Decimal(str(cantidad)),
                    costo_unitario=costo_unitario,
                    subtotal=subtotal
                )
                db.add(item)
                total_compra += subtotal
            
            compra.monto_total = total_compra
            total_gastado += total_compra
            compras_creadas += 1
        
        db.commit()
        print(f"✅ Creadas {compras_creadas} compras de demostración")
        print(f"💸 Total gastado (demo): ${total_gastado:,.0f} CLP")
        return compras_creadas, float(total_gastado)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Poblando base de datos con datos de demostración...\n")
    
    ventas_count, ventas_total = seed_demo_sales()
    compras_count, compras_total = seed_demo_purchases()
    
    utilidad = ventas_total - compras_total
    
    print(f"\n📊 RESUMEN:")
    print(f"   Ventas: {ventas_count} órdenes - ${ventas_total:,.0f} CLP")
    print(f"   Gastos: {compras_count} compras - ${compras_total:,.0f} CLP")
    print(f"   {'🟢 Utilidad' if utilidad > 0 else '🔴 Pérdida'}: ${utilidad:,.0f} CLP")
    print(f"\n✅ Datos de demostración listos!")
    print(f"🌐 Abre el Dashboard en: http://localhost:5173")
