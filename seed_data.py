from app.database import SessionLocal, engine
from app import models
import uuid
from datetime import datetime, timedelta
import random

# Inicializar DB
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed_database():
    print("☕ Preparando la máquina de espresso... (Generando datos)")

    # 1. EL MENÚ (Productos)
    categorias = {
        "Cafetería Caliente": ["Espresso", "Doppio", "Americano", "Cappuccino", "Latte", "Flat White", "Mocaccino"],
        "Cafetería Fría": ["Iced Latte", "Cold Brew", "Frappuccino Caramelo", "Frappuccino Moka", "Affogato"],
        "Pastelería": ["Croissant de Almendras", "Medialuna", "Brownie con Helado", "Cheesecake de Frutos Rojos", "Pie de Limón", "Torta de Zanahoria"],
        "Sándwiches": ["Ave Palta", "Barros Luco", "Ciabatta Jamón Serrano", "Tostadas con Huevo"],
        "Bebidas": ["Jugo Natural Naranja", "Limonada Menta Jengibre", "Agua Mineral", "Coca Cola Zero"]
    }

    productos_db = []
    print("   🥐 Horneando productos...")
    for cat, items in categorias.items():
        for nombre in items:
            # Precio aleatorio realista
            precio = random.choice([2500, 3200, 3800, 4500, 4900, 5500]) if "Sándwiches" in cat else random.choice([1800, 2200, 2800, 3500, 3900])
            prod = models.Producto(
                nombre=nombre,
                categoria=cat,
                ventas_totales=0,
                ingresos_totales=0
            )
            db.add(prod)
            productos_db.append(prod)
    
    db.commit()

    # 2. CLIENTES FRECUENTES
    nombres = ["Valentina", "Sebastián", "Camila", "Matías", "Sofía", "Nicolás", "Isabella", "Benjamín", "Lucía", "Tomás", "Cliente Casual"]
    clientes_db = []
    print("   👥 Abriendo las puertas a los clientes...")
    for nombre in nombres:
        cli = models.Cliente(
            nombre=f"{nombre} {random.choice(['González', 'Muñoz', 'Rojas', 'Díaz', 'Pérez'])}" if nombre != "Cliente Casual" else nombre,
            email=f"{nombre.lower()}@gmail.com" if nombre != "Cliente Casual" else None,
            pedidos_totales=0,
            gasto_total=0
        )
        db.add(cli)
        clientes_db.append(cli)
    db.commit()

    # 3. SIMULAR 30 DÍAS DE VENTAS
    print("   📉 Simulando el mes de enero...")
    fecha_inicio = datetime.utcnow() - timedelta(days=30)
    
    canales = ["Salon", "Salon", "Salon", "Delivery", "Para Llevar"] # Más peso a Salon
    metodos = ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"]
    
    total_ventas_count = 0

    for dia in range(31):
        fecha_actual = fecha_inicio + timedelta(days=dia)
        
        # Ventas por día (entre 15 y 40 tickets)
        num_ventas = random.randint(15, 45)
        
        # Más ventas viernes y sabado
        if fecha_actual.weekday() >= 4: 
            num_ventas += 15

        for _ in range(num_ventas):
            # Hora aleatoria (08:00 a 20:00)
            hora = random.randint(8, 20)
            minuto = random.randint(0, 59)
            fecha_venta = fecha_actual.replace(hour=hora, minute=minuto)
            
            # Elegir cliente y canal
            cliente = random.choice(clientes_db)
            canal = random.choice(canales)
            
            # Crear Venta
            venta = models.Venta(
                fudo_ticket_id=f"T-{uuid.uuid4().hex[:6].upper()}",
                fecha=fecha_venta,
                canal=canal,
                metodo_pago=random.choice(metodos),
                mesero=random.choice(["Juan", "Ana", "Pedro"]),
                caja="Caja Principal",
                mesa=str(random.randint(1, 15)) if canal == "Salon" else None,
                estado="cerrada",
                cliente_id=cliente.id
            )
            db.add(venta)
            db.flush()

            # Agregar Items a la venta (1 a 4 productos)
            num_items = random.randint(1, 4)
            total_venta = 0
            
            items_elegidos = random.sample(productos_db, num_items)
            
            for prod in items_elegidos:
                cantidad = 1
                subtotal = prod.ingresos_totales # Usamos esto temporalmente para guardar el precio base, ups mala practica en seed, mejor recalculo
                # Hack rapido: obtener precio base del 'random' anterior es dificil aqui sin guardarlo.
                # Asignaremos precio fresco
                precio_unit = random.choice([2000, 3000, 4000]) # Precio fake para el item
                
                subtotal = precio_unit * cantidad
                
                item = models.ItemVenta(
                    venta_id=venta.id,
                    producto_id=prod.id,
                    producto_nombre=prod.nombre,
                    categoria=prod.categoria,
                    cantidad=cantidad,
                    precio_unitario=precio_unit,
                    subtotal=subtotal
                )
                db.add(item)
                
                # Actualizar Stats Producto
                prod.ventas_totales += cantidad
                prod.ingresos_totales += subtotal
                
                total_venta += subtotal
            
            # Actualizar Venta y Cliente
            venta.importe_total = total_venta
            cliente.pedidos_totales += 1
            cliente.gasto_total += total_venta
            cliente.ultima_compra = fecha_venta
            
            total_ventas_count += 1
            
    db.commit()
    print(f"\n✨ ¡Magia terminada! Se generaron {total_ventas_count} ventas históricas.")
    print("   El sistema ahora tiene vida. 🚀")

if __name__ == "__main__":
    seed_database()
