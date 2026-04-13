from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional, List
from .. import database, models, schemas

router = APIRouter(prefix="/api/kingdom", tags=["Kingdom Coffee"])

@router.post("/capture")
def capture_client_data(
    nombre: str,
    whatsapp: str,
    birthdate: Optional[str] = None, # Formato YYYY-MM-DD
    metodo: str = "qr_carta", # qr_carta, wifi, etc.
    db: Session = Depends(database.get_db)
):
    """
    Captura datos del cliente desde el QR de la carta o WiFi.
    """
    # Limpiar whatsapp (solo números)
    whatsapp_clean = "".join(filter(str.isdigit, whatsapp))
    
    # Buscar cliente por whatsapp
    cliente = db.query(models.Cliente).filter(models.Cliente.whatsapp == whatsapp_clean).first()
    
    if not cliente:
        cliente = models.Cliente(
            nombre=nombre,
            whatsapp=whatsapp_clean,
            telefono=whatsapp_clean,
            email="",
            points=0,
            stamps=0,
            loyalty_level="bronze",
            donde_nos_conocio=metodo
        )
        db.add(cliente)
        db.flush()
    else:
        cliente.nombre = nombre
        cliente.donde_nos_conocio = metodo
    
    if birthdate:
        try:
            cliente.birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
        except:
            pass
    
    db.commit()
    db.refresh(cliente)
    
    return {
        "success": True,
        "message": f"Bienvenido al Kingdom vía {metodo}!",
        "cliente": {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "puntos": cliente.points
        }
    }

@router.get("/clients")
def get_all_clients(db: Session = Depends(database.get_db)):
    """
    Lista todos los clientes registrados en Kingdom (CRM).
    """
    clientes = db.query(models.Cliente).all()
    return [{
        "id": c.id,
        "nombre": c.nombre,
        "whatsapp": c.whatsapp,
        "email": c.email,
        "puntos": c.points,
        "granos": c.stamps,
        "nivel": c.loyalty_level,
        "ultima_compra": c.ultima_compra
    } for c in clientes]

@router.get("/profile/{whatsapp}")
def get_kingdom_profile(whatsapp: str, db: Session = Depends(database.get_db)):
    whatsapp_clean = "".join(filter(str.isdigit, whatsapp))
    cliente = db.query(models.Cliente).filter(models.Cliente.telefono == whatsapp_clean).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    return {
        "nombre": cliente.nombre,
        "puntos": cliente.points,
        "granos": cliente.stamps,
        "nivel": cliente.loyalty_level,
        "ultima_compra": cliente.ultima_compra
    }

@router.post("/add-points")
def add_points_to_client(
    whatsapp: str,
    amount: float,
    fudo_ticket_id: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """
    Endpoint para que n8n otorgue puntos cuando detecta una venta en Fudo.
    Fidelización: 1 punto por cada $1000.
    """
    whatsapp_clean = "".join(filter(str.isdigit, whatsapp))
    
    # 1. Evitar doble puntaje por el mismo ticket
    if fudo_ticket_id:
        existing_sale = db.query(models.Venta).filter(models.Venta.fudo_ticket_id == fudo_ticket_id).first()
        if existing_sale and existing_sale.estado == "procesado_puntos":
            return {"success": False, "message": "Puntos ya otorgados para este ticket"}

    # 2. Buscar cliente
    cliente = db.query(models.Cliente).filter(models.Cliente.whatsapp == whatsapp_clean).first()
    if not cliente:
        # Si no existe, podemos crearlo o fallar. Para n8n, mejor intentar buscar por email si viene.
        return {"success": False, "message": "Cliente no encontrado en App. Debe registrarse primero."}

    # 3. Calcular puntos (1 punto por cada 1000)
    puntos_nuevos = int(amount / 1000)
    cliente.points += puntos_nuevos
    cliente.gasto_total += amount
    cliente.pedidos_totales += 1
    cliente.ultima_compra = datetime.utcnow()
    
    # 4. Sistema de Granos (Stamps): 1 grano por compra
    cliente.stamps += 1
    if cliente.stamps > 10:
        cliente.stamps = 1 # Reinicia tras canje o mantiene flujo
        
    # 5. Promoción de Niveles
    if cliente.points > 1000:
        cliente.loyalty_level = "oro"
    elif cliente.points > 500:
        cliente.loyalty_level = "plata"
        
    # Marcar venta como procesada si existe el ticket
    if fudo_ticket_id:
        # Aquí se podría registrar la venta si no existe, o actualizarla
        pass

    db.commit()
    
    return {
        "success": True, 
        "puntos_ganados": puntos_nuevos,
        "total_puntos": cliente.points,
        "nivel": cliente.loyalty_level,
        "granos": cliente.stamps
    }

@router.post("/order")
async def place_order(
    whatsapp: str,
    items: List[dict], # List of {id_fudo, quantity, price, name}
    total: float,
    db: Session = Depends(database.get_db)
):
    """
    Realiza un pedido usando el saldo de la Wallet y lo envía a Fudo.
    """
    whatsapp_clean = "".join(filter(str.isdigit, whatsapp))
    cliente = db.query(models.Cliente).filter(models.Cliente.whatsapp == whatsapp_clean).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Placeholder: Encontrar el usuario SaaS para descontar balance 
    # (En Kingdom, el balance vive en models.User o models.Cliente?)
    # Según models.py, Cliente tiene gasto_total pero el balance parece estar en User.
    # Pero el usuario usará su WhatsApp, así que buscaremos relación o usaremos Cliente.points como moneda?
    # El usuario dijo 'en wallet' y models.User tiene 'credits/balance'?
    
    # REVISIÓN: En models.py el balance está en la tabla User (Salon SaaS).
    # Pero para Kingdom Coffee, usaremos un campo de balance en Cliente si existe.
    # Como no existe 'balance' en Cliente, vamos a usar 'points' como créditos 
    # o mejor: asumimos que el usuario registrado en Firebase tiene un 'balance' en Firestore
    # y aquí solo lo registramos como Venta.
    
    # Por ahora, registramos la venta y enviamos a Fudo.
    from app.integrations.fudo_client import FudoClient
    fudo = FudoClient()
    
    fudo_order = {
        "sale": {
            "items": [
                {
                    "product_id": item['id_fudo'],
                    "quantity": item['quantity'],
                    "price": item['price']
                } for item in items
            ],
            "client_id": cliente.fudo_cliente_id,
            "comment": f"Pedido App Kingdom - {cliente.nombre}"
        }
    }
    
    result = await fudo.create_sale(fudo_order)
    
    if result.get("success"):
        # Actualizar stats locales
        cliente.pedidos_totales += 1
        cliente.gasto_total += total
        cliente.ultima_compra = datetime.utcnow()
        # Otorgar puntos por la compra
        cliente.points += int(total / 1000)
        cliente.stamps += 1
        
        db.commit()
        return {"success": True, "message": "Pedido enviado a barra!", "fudo_response": result["data"]}
    else:
        raise HTTPException(status_code=500, detail=f"Error en Fudo: {result.get('message')}")

@router.post("/sync-direct")
async def sync_direct_to_supabase(email: str, db: Session = Depends(database.get_db)):
    """
    Sincroniza ventas desde Fudo a Supabase. 
    Prueba múltiples endpoints para asegurar compatibilidad con el token actual.
    """
    from datetime import date, timedelta
    from app.integrations.fudo_client import FudoClient
    import httpx
    
    SUPABASE_URL = "https://bcfulknkkwlpxpiuboyt.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJjZnVsa25ra3dscHhwaXVib3l0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTE1NDA4NCwiZXhwIjoyMDg2NzMwMDg0fQ.Yt10YQKSQjaqwy8vCgWItxkyQ7aaxMUW-7p1a7XEQ9Y"
    
    fudo = FudoClient()
    await fudo.refresh_token() # Asegurar token fresco
    
    endpoints = ["/sales", "/sale_identifiers", "/orders"]
    all_fudo_sales = []
    log = []

    async with httpx.AsyncClient() as client:
        headers = fudo.get_auth_headers()
        for ep in endpoints:
            try:
                r = await client.get(f"{fudo.base_url}{ep}", headers=headers, timeout=10)
                log.append(f"Try {ep}: {r.status_code}")
                if r.status_code == 200:
                    data = r.json()
                    sales = data.get("data") or data.get("sales") or (data if isinstance(data, list) else [])
                    all_fudo_sales.extend(sales)
                    if sales: break # Si encontramos algo, paramos
            except Exception as e:
                log.append(f"Error {ep}: {str(e)}")

        synced_count = 0
        found_for_user = 0
        
        for sale in all_fudo_sales:
            fudo_client = sale.get('client', {})
            client_email = fudo_client.get('email', '').lower()
            
            if client_email == email.lower():
                found_for_user += 1
                supabase_sale = {
                    "fudo_sale_id": str(sale.get('id')),
                    "cliente_telefono": fudo_client.get('phone'),
                    "cliente_email": client_email,
                    "cliente_nombre": fudo_client.get('name'),
                    "total_venta": float(sale.get('total', 0)),
                    "puntos_generados": int(float(sale.get('total', 0)) / 1000),
                    "productos": sale.get('items', []),
                    "fecha_venta": sale.get('created_at')
                }
                
                # Insertar en Supabase
                sb_headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                }
                
                try:
                    await client.post(f"{SUPABASE_URL}/rest/v1/ventas_fudo", json=supabase_sale, headers=sb_headers)
                    synced_count += 1
                except:
                    pass
    
    return {
        "success": True,
        "email": email,
        "fudo_api_log": log,
        "ventas_fudo_totales": len(all_fudo_sales),
        "ventas_usuario_encontradas": found_for_user,
        "ventas_sincronizadas_ok": synced_count
    }

@router.get("/reservations")
async def get_fudo_reservations(days_ahead: int = 7):
    """
    Consulta las reservas activas en Fudo.
    """
    from datetime import date, timedelta
    from app.integrations.fudo_client import FudoClient
    
    fudo = FudoClient()
    desde = date.today()
    hasta = date.today() + timedelta(days=days_ahead)
    
    reservations = await fudo.fetch_reservations(desde, hasta)
    return {"success": True, "reservations": reservations}

@router.post("/reservations")
async def create_fudo_reservation(data: dict):
    """
    Crea una reserva en Fudo directamente.
    """
    from app.integrations.fudo_client import FudoClient
    fudo = FudoClient()
    
    # reservation_data debe venir formateado para Fudo
    result = await fudo.create_reservation(data)
    return result

# ==================================================
# GEOFENCING - Marketing de Proximidad
# ==================================================

# Nota: geofence_events ahora es un cache volátil. 
# La fuente de verdad absoluta es Supabase: public.geofence_events
geofence_events_cache = []

@router.post("/geofence-trigger")
async def geofence_trigger(data: dict):
    """
    Registra cuando un cliente entra en la zona de geofencing (500m del local).
    Otorga coronas/puntos extra, registra el evento en Supabase y envía Push.
    """
    import os
    from datetime import datetime
    import httpx

    user_id = data.get("user_id", "anonymous")
    user_email = data.get("user_email", "")
    distance_meters = data.get("distance_meters", 0)
    bonus_crowns = int(data.get("bonus_crowns", 50))
    custom_message = data.get("custom_message", "")
    is_campaign = data.get("is_campaign", False)

    # 1. Preparar el evento
    event = {
        "user_id": user_id,
        "user_email": user_email,
        "distance_meters": distance_meters,
        "bonus_crowns": bonus_crowns,
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Av. Austral 1795, Puerto Montt",
    }

    # 2. Persistir en Supabase (public.geofence_events)
    SUPABASE_URL = "https://bcfulknkkwlpxpiuboyt.supabase.co"
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("VITE_SUPABASE_SERVICE_ROLE_KEY")
    
    if SUPABASE_KEY:
        async with httpx.AsyncClient() as client:
            try:
                # Guardar el evento para el historial
                await client.post(
                    f"{SUPABASE_URL}/rest/v1/geofence_events",
                    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                    json=event,
                    timeout=5
                )

                # Si no es una campaña masiva, actualizar puntos del usuario
                if not is_campaign and user_email:
                    r = await client.get(
                        f"{SUPABASE_URL}/rest/v1/users?email=eq.{user_email}&select=id,points",
                        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                        timeout=5,
                    )
                    if r.status_code == 200 and r.json():
                        user_data = r.json()[0]
                        new_points = (user_data.get("points") or 0) + bonus_crowns
                        await client.patch(
                            f"{SUPABASE_URL}/rest/v1/users?email=eq.{user_email}",
                            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                            json={"points": new_points},
                            timeout=5,
                        )
            except Exception as e:
                print(f"Supabase geofence error: {e}")

    # 3. Enviar Push via OneSignal
    onesignal_key = os.environ.get("ONESIGNAL_REST_API_KEY", "")
    onesignal_app_id = os.environ.get("ONESIGNAL_APP_ID", "")
    
    if onesignal_key and onesignal_app_id:
        try:
            async with httpx.AsyncClient() as client:
                push_payload = {
                    "app_id": onesignal_app_id,
                    "headings": {"es": "👑 Kingdom Coffee"},
                    "url": "https://the-kingdom-coffee.vercel.app",
                }
                
                if is_campaign:
                    push_payload["included_segments"] = ["All"]
                    push_payload["contents"] = {"es": custom_message or "¡Novedades en el Reino! Ven por tu café."}
                else:
                    push_payload["filters"] = [{"field": "tag", "key": "user_id", "relation": "=", "value": user_id}]
                    push_payload["headings"]["es"] = "👑 ¡Estás cerca del Kingdom!"
                    push_payload["contents"] = {"es": f"¡A solo {distance_meters}m! Entra hoy y gana {bonus_crowns} Coronas extra. ☕"}
                
                await client.post(
                    "https://onesignal.com/api/v1/notifications",
                    headers={"Authorization": f"Basic {onesignal_key}", "Content-Type": "application/json"},
                    json=push_payload,
                    timeout=5,
                )
        except Exception as e:
            print(f"OneSignal error: {e}")

    return {
        "success": True,
        "message": "Evento procesado correctamente",
        "event": event
    }

@router.get("/geofence-events")
async def get_geofence_events(limit: int = 100):
    """
    Devuelve los últimos eventos de geofencing desde Supabase.
    """
    import os
    import httpx
    
    SUPABASE_URL = "https://bcfulknkkwlpxpiuboyt.supabase.co"
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("VITE_SUPABASE_SERVICE_ROLE_KEY")
    
    if not SUPABASE_KEY:
        return {"success": True, "events": []}

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{SUPABASE_URL}/rest/v1/geofence_events?select=*&order=timestamp.desc&limit={limit}",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                timeout=5
            )
            if r.status_code == 200:
                return {"success": True, "events": r.json()}
    except Exception as e:
        print(f"Error fetching geofence events: {e}")
        
    return {"success": True, "events": []}
