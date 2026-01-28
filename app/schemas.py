from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# --- AUTH SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool
    plan_type: str = "demo"
    trial_end_at: Optional[datetime] = None
    subscription_active: bool = False
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- FUDO IMPORT SCHEMAS (INPUT) ---

class ClienteImport(BaseModel):
    fudo_cliente_id: Optional[str] = None
    nombre: Optional[str] = "Cliente General"
    telefono: Optional[str] = None
    email: Optional[str] = None

class ItemVentaImport(BaseModel):
    producto_nombre: str
    categoria: str
    cantidad: float
    precio_unitario: float
    subtotal: float

class VentaImport(BaseModel):
    fudo_ticket_id: str
    fecha: datetime
    canal: str
    metodo_pago: str
    mesero: Optional[str] = None
    caja: Optional[str] = None
    mesa: Optional[str] = None
    importe_total: float
    estado: str
    cliente: Optional[ClienteImport] = None
    items: List[ItemVentaImport]

# --- RESPONSE SCHEMAS (OUTPUT) ---

class ItemVentaResponse(BaseModel):
    id: str
    producto_nombre: str
    categoria: str
    cantidad: float
    precio_unitario: float
    subtotal: float
    class Config:
        from_attributes = True

class ClienteResponse(BaseModel):
    id: str
    nombre: str
    email: Optional[str]
    pedidos_totales: int
    gasto_total: float
    class Config:
        from_attributes = True

class VentaResponse(BaseModel):
    id: str
    fudo_ticket_id: str
    fecha: datetime
    canal: str
    metodo_pago: str
    importe_total: float
    estado: str
    mesero: Optional[str]
    items: List[ItemVentaResponse] = []
    cliente: Optional[ClienteResponse] = None
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    ventas_total: float
    cantidad_ventas: int
    ticket_promedio: float
    ventas_por_canal: List[dict] # [{"canal": "salon", "total": 1000}]
    top_productos: List[dict]
    top_clientes: List[dict]

class ProductoRanking(BaseModel):
    id: str
    nombre: str
    categoria: str
    ventas_totales: int
    ingresos_totales: float
    class Config:
        from_attributes = True

# --- SALON SAAS SCHEMAS ---

# Stylist
class StylistBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    color: Optional[str] = "#000000"
    avatar: Optional[str] = None
    active: bool = True

class StylistCreate(StylistBase):
    pass

class Stylist(StylistBase):
    id: str
    owner_id: str
    class Config:
        from_attributes = True

# Service
class ServiceBase(BaseModel):
    name: str
    duration: int
    price: float
    color: Optional[str] = "#000000"

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: str
    owner_id: str
    class Config:
        from_attributes = True

# SalonClient
class SalonClientBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

class SalonClientCreate(SalonClientBase):
    pass

class SalonClient(SalonClientBase):
    id: str
    owner_id: str
    last_visit: Optional[datetime] = None
    class Config:
        from_attributes = True

# Appointment
class AppointmentBase(BaseModel):
    stylist_id: str
    client_id: str
    service_id: Optional[str] = None
    title: str
    start_time: datetime
    end_time: datetime
    status: str = "pending"
    notes: Optional[str] = None
    price: Optional[float] = None

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: str
    owner_id: str
    class Config:
        from_attributes = True
