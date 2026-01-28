import uuid
from sqlalchemy import Column, String, Boolean, Integer, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
from .database import Base

# --- FASE 1: FUDO CORE ---

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fudo_ticket_id = Column(String, unique=True, index=True)
    fecha = Column(DateTime(timezone=True))
    canal = Column(String(50))  # salon, delivery, tienda_online, whatsapp, otros
    metodo_pago = Column(String(50))
    mesero = Column(String(100))
    caja = Column(String(50))
    mesa = Column(String(20))
    importe_total = Column(Numeric(12, 2))
    estado = Column(String(20))  # abierta, cerrada, anulada
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=True)
    creado_en = Column(DateTime(timezone=True), default=datetime.utcnow)
    actualizado_en = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    cliente = relationship("Cliente", back_populates="ventas")
    items = relationship("ItemVenta", back_populates="venta", cascade="all, delete-orphan")
    documento_tributario = relationship("DocumentoTributario", back_populates="venta", uselist=False)

class ItemVenta(Base):
    __tablename__ = "items_venta"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    venta_id = Column(String, ForeignKey("ventas.id", ondelete="CASCADE"))
    producto_id = Column(String, ForeignKey("productos.id"), nullable=True)
    producto_nombre = Column(String(200))
    categoria = Column(String(100))
    cantidad = Column(Numeric(10, 2))
    precio_unitario = Column(Numeric(12, 2))
    subtotal = Column(Numeric(12, 2))

    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto", back_populates="items_vendidos")

class Producto(Base):
    __tablename__ = "productos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fudo_producto_id = Column(String, nullable=True)
    nombre = Column(String(200), unique=True, index=True)
    categoria = Column(String(100))
    activo = Column(Boolean, default=True)
    ventas_totales = Column(Integer, default=0)
    ingresos_totales = Column(Numeric(14, 2), default=0)
    ultima_actualizacion = Column(DateTime(timezone=True), default=datetime.utcnow)

    items_vendidos = relationship("ItemVenta", back_populates="producto")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fudo_cliente_id = Column(String, nullable=True, unique=True)
    nombre = Column(String(200))
    telefono = Column(String(20))
    email = Column(String(200))
    pedidos_totales = Column(Integer, default=0)
    gasto_total = Column(Numeric(14, 2), default=0)
    ultima_compra = Column(DateTime(timezone=True))

    ventas = relationship("Venta", back_populates="cliente")

# --- FASE 2 & 3: EBILL & RUKA (Placeholders) ---

class DocumentoTributario(Base):
    __tablename__ = "documentos_tributarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ebill_document_id = Column(String, unique=True)
    tipo_documento = Column(String(50)) # boleta, factura
    folio = Column(String(50))
    fecha_emision = Column(DateTime(timezone=True))
    rut_cliente = Column(String(20))
    razon_social = Column(String(200))
    monto_total = Column(Numeric(14, 2))
    estado = Column(String(50))
    venta_id = Column(String, ForeignKey("ventas.id"), nullable=True, unique=True)
    creado_en = Column(DateTime(timezone=True), default=datetime.utcnow)

    venta = relationship("Venta", back_populates="documento_tributario")

class Compra(Base):
    __tablename__ = "compras"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ruka_compra_id = Column(String, unique=True)
    fecha = Column(DateTime(timezone=True))
    proveedor_nombre = Column(String(200))
    monto_total = Column(Numeric(14, 2))
    creado_en = Column(DateTime(timezone=True), default=datetime.utcnow)

    items = relationship("ItemCompra", back_populates="compra", cascade="all, delete-orphan")

class ItemCompra(Base):
    __tablename__ = "items_compra"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    compra_id = Column(String, ForeignKey("compras.id", ondelete="CASCADE"))
    insumo_nombre = Column(String(200))
    cantidad = Column(Numeric(12, 3))
    costo_unitario = Column(Numeric(14, 4))
    subtotal = Column(Numeric(14, 2))

    compra = relationship("Compra", back_populates="items")

# --- AUTH ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Salon Profile Fields
    business_name = Column(String, nullable=True)
    business_logo = Column(Text, nullable=True) # Base64
    created_at = Column(DateTime, default=datetime.utcnow)

    # Subscription Fields
    plan_type = Column(String, default="demo") # 'demo', 'basic', 'pro'
    trial_start_at = Column(DateTime, default=datetime.utcnow)
    trial_end_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    subscription_active = Column(Boolean, default=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # Relationships (SaaS)
    stylists = relationship("Stylist", back_populates="owner")
    services = relationship("Service", back_populates="owner")
    appointments = relationship("Appointment", back_populates="owner")
    clients = relationship("SalonClient", back_populates="owner")

# --- SALON SAAS CORE ---

class Stylist(Base):
    __tablename__ = "stylists"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id")) # Multi-tenancy
    name = Column(String)
    specialty = Column(String)
    color = Column(String)
    avatar = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    
    owner = relationship("User", back_populates="stylists")
    appointments = relationship("Appointment", back_populates="stylist")

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    duration = Column(Integer) # Minutes
    price = Column(Numeric(10, 2))
    color = Column(String)

    owner = relationship("User", back_populates="services")

class SalonClient(Base):
    """Specific client table for Salon app to separate from Fudo clients if needed."""
    __tablename__ = "salon_clients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    last_visit = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="clients")
    appointments = relationship("Appointment", back_populates="client")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"))
    
    stylist_id = Column(String, ForeignKey("stylists.id"))
    client_id = Column(String, ForeignKey("salon_clients.id"))
    service_id = Column(String, ForeignKey("services.id"), nullable=True) # Optional link
    
    title = Column(String) # Service Name snapshot
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String, default="pending") # pending, confirmed, attended, no_show, cancelled
    notes = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    
    owner = relationship("User", back_populates="appointments")
    stylist = relationship("Stylist", back_populates="appointments")
    client = relationship("SalonClient", back_populates="appointments")
