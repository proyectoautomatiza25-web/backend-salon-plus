from fastapi import APIRouter, HTTPException, Query
from datetime import date, datetime, timedelta
from typing import Optional
import asyncio

from app.integrations.fudo_client import FudoClient

router = APIRouter()


@router.get("/test-connection")
async def test_fudo_connection():
    """
    Prueba la conexión con la API de Fudo.
    
    Returns:
        dict: Estado de la conexión
    """
    try:
        client = FudoClient()
        result = await client.test_connection()
        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/product-categories")
async def fetch_fudo_categories():
    """Obtiene categorías de productos."""
    try:
        client = FudoClient()
        categories = await client.fetch_categories()
        if not categories:
            # Fallback mock categories
            categories = [
                {"id": "c1", "name": "CAFÉ DE ESPECIALIDAD"},
                {"id": "c2", "name": "PASTELERÍA RECOLETA"},
                {"id": "c3", "name": "SANDWICHES REALES"},
                {"id": "c4", "name": "BEBIDAS FRÍAS"}
            ]
        return {"success": True, "categories": categories}
    except Exception as e:
        return {"success": True, "categories": [
            {"id": "c1", "name": "CAFÉ DE ESPECIALIDAD"},
            {"id": "c2", "name": "PASTELERÍA RECOLETA"}
        ]}

@router.get("/tables")
async def fetch_fudo_tables():
    """Obtiene el estado de las mesas."""
    try:
        client = FudoClient()
        tables = await client.fetch_tables()
        return {"success": True, "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/products")
async def fetch_fudo_products(use_db: bool = True):
    """Obtiene productos sincronizados o desde la API."""
    if use_db:
        from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
        import httpx
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{SUPABASE_URL}/rest/v1/productos_fudo?select=*", headers=headers)
            if r.status_code == 200:
                return {"success": True, "products": r.json()}

    try:
        client = FudoClient()
        products = await client.fetch_products()
        return {"success": True, "products": products or []}
    except Exception as e:
        return {"success": False, "products": [], "error": str(e)}

@router.get("/orders")
async def fetch_fudo_orders(use_db: bool = True, days: int = 30):
    """Obtiene ventas sincronizadas para el Dashboard."""
    if use_db:
        from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
        import httpx
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        async with httpx.AsyncClient() as client:
            # Traemos los de los últimos X días para que se vea algo
            r = await client.get(f"{SUPABASE_URL}/rest/v1/ventas_fudo?select=*&order=fecha_venta.desc&limit=2000", headers=headers)
            if r.status_code == 200:
                return {"success": True, "orders": r.json()}

    return {"success": True, "orders": []}

@router.get("/providers")
async def fetch_fudo_providers():
    """Obtiene la lista de proveedores desde Fudo."""
    try:
        client = FudoClient()
        providers = await client.fetch_providers()
        return {"success": True, "providers": providers or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.api_route("/sync-menu", methods=["GET", "POST"])
async def sync_fudo_menu():
    """Sincroniza el catálogo completo de Fudo con Supabase."""
    from app.services.fudo_sync import FudoSyncService
    return await FudoSyncService.sync_menu()

@router.post("/claim-sale")
async def claim_fudo_sale(data: dict):
    """
    Permite a un usuario de la App reclamar una venta usando el ID del ticket.
    """
    order_id = data.get("order_id")
    whatsapp = data.get("whatsapp")
    email = data.get("email")
    
    identifier = whatsapp or email
    
    if not order_id or not identifier:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios (order_id, whatsapp o email)")

    from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
    import httpx
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        # 1. Verificar si la venta existe en nuestra DB
        r = await client.get(f"{SUPABASE_URL}/rest/v1/ventas_fudo?fudo_order_id=eq.{order_id}&select=*", headers=headers)
        
        if r.status_code != 200 or not r.json():
            from app.services.fudo_sync import FudoSyncService
            await FudoSyncService.sync_sales(hours=168)
            r = await client.get(f"{SUPABASE_URL}/rest/v1/ventas_fudo?fudo_order_id=eq.{order_id}&select=*", headers=headers)
            
            if r.status_code != 200 or not r.json():
                raise HTTPException(status_code=404, detail="No pudimos encontrar ese número de ticket. Verifica que el ID sea correcto.")

        venta = r.json()[0]
        
        # 2. Verificar si ya tiene dueño
        if venta.get("cliente_telefono"):
            if venta["cliente_telefono"] == identifier:
                return {"success": True, "message": "Esta venta ya está vinculada a tu cuenta."}
            raise HTTPException(status_code=400, detail="Este ticket ya fue reclamado por otro usuario.")

        # 3. Vincular (usamos cliente_telefono para guardar el identificador sea cual sea)
        update_res = await client.patch(
            f"{SUPABASE_URL}/rest/v1/ventas_fudo?fudo_order_id=eq.{order_id}",
            json={"cliente_telefono": identifier},
            headers=headers
        )
        
        if update_res.status_code in [200, 204]:
            return {
                "success": True, 
                "message": "¡Venta vinculada con éxito!", 
                "puntos": venta.get("puntos_generados", 0)
            }
        
    raise HTTPException(status_code=500, detail="Error al procesar el reclamo de puntos.")

@router.post("/reclamar-boleta")
async def reclamar_boleta_por_folio(data: dict):
    """
    NUEVO: Permite reclamar puntos usando FOLIO SII y MONTO TOTAL.
    Es instantáneo porque busca en la base de datos pre-sincronizada.
    """
    folio = str(data.get("folio")).strip()
    monto = float(data.get("monto") or 0)
    whatsapp = data.get("whatsapp")
    
    if not folio or not monto or not whatsapp:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios: folio, monto y whatsapp.")

    from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
    import httpx
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    venta = None
    fudo_id_real = None
    monto_validado = 0

    async with httpx.AsyncClient() as client:
        # 1. Búsqueda por Folio (si se ingresó)
        if folio and folio != "0":
            query_params = f"or=(fudo_order_id.eq.{folio},folio_sii.eq.{folio})&cliente_telefono=is.null&order=fecha_venta.desc"
            r_venta = await client.get(f"{SUPABASE_URL}/rest/v1/ventas_fudo?{query_params}&select=*", headers=headers)
            
            if r_venta.status_code == 200 and r_venta.json():
                venta = r_venta.json()[0]
                fudo_id_real = venta.get("fudo_order_id")
                monto_validado = float(venta.get("monto_total", 0))

        # 2. PLAN MAESTRO: Búsqueda por Monto Exacto (Últimas 48h)
        # Ampliamos a 48h para evitar líos de zona horaria entre el servidor y Chile
        desde_str = (datetime.now() - timedelta(hours=48)).strftime("%Y-%m-%d")
        r_monto = await client.get(
            f"{SUPABASE_URL}/rest/v1/ventas_fudo?monto_total=eq.{monto}&cliente_telefono=is.null&fecha_venta=gte.{desde_str}T00:00:00",
            headers=headers
        )
        if r_monto.status_code == 200 and r_monto.json():
            venta = r_monto.json()[0]
            fudo_id_real = venta.get("fudo_order_id")
            monto_validado = float(venta.get("monto_total", 0))

        # 3. Si no encontramos nada, sincronización profunda y búsqueda en órdenes vivas
        if not venta:
            from app.services.fudo_sync import FudoSyncService
            await FudoSyncService.sync_sales(hours=1) 
            
            # Reintento final por monto con rango amplio
            r_retry = await client.get(
                f"{SUPABASE_URL}/rest/v1/ventas_fudo?monto_total=eq.{monto}&cliente_telefono=is.null&fecha_venta=gte.{desde_str}T00:00:00",
                headers=headers
            )
            if r_retry.status_code == 200 and r_retry.json():
                venta = r_retry.json()[0]
                fudo_id_real = venta.get("fudo_id_real") or venta.get("fudo_order_id")
                monto_validado = float(venta.get("monto_total", 0))

        # 4. ÚLTIMO RECURSO: Búsqueda Manual Directa en Fudo (Solo si tenemos el Folio)
        if not venta and folio:
            from app.integrations.fudo_client import FudoClient
            fudo = FudoClient()
            await fudo.refresh_token()
            fudo_order = await fudo.fetch_order_by_number(folio)
            if fudo_order:
                venta = fudo_order
                fudo_id_real = fudo_order.get("id")
                # Calcular monto de la orden viva
                monto_validado = 0
                for it in fudo_order.get("additions", []):
                    if not it.get("cancellationComment"):
                        monto_validado += float(it.get("price", 0)) * float(it.get("count", 1))

        if not venta:
            raise HTTPException(status_code=404, detail="[v2.1] No encontramos ninguna venta pendiente hoy. Verifica el monto.")

        # 4. Vincular y otorgar puntos
        puntos = int(monto_validado / 10000)
        if puntos < 1: puntos = 1
        
        # Marcar venta como reclamada (Usamos UPSERT por si la venta es nueva de Fudo Live)
        upsert_payload = {
            "fudo_order_id": str(fudo_id_real),
            "monto_total": monto_validado,
            "cliente_telefono": whatsapp,
            "puntos_generados": puntos,
            "fecha_venta": venta.get("createdAt") or datetime.now().isoformat()
        }
        
        await client.post(
            f"{SUPABASE_URL}/rest/v1/ventas_fudo",
            json=upsert_payload,
            headers={**headers, "Prefer": "resolution=merge-duplicates"}
        )
        
        # Incrementar puntos del usuario
        await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/increment_user_points",
            json={"u_whatsapp": whatsapp, "inc_points": puntos},
            headers=headers
        )

        return {
            "success": True,
            "message": "¡Venta validada con éxito!",
            "puntos": puntos,
            "monto": monto_validado,
            "id": fudo_id_real,
            "fecha": venta.get("fecha_venta")
        }

@router.api_route("/sync-sales", methods=["GET", "POST"])
async def sync_fudo_sales(hours: int = 24):
    """Sincroniza las ventas recientes de Fudo con Supabase."""
    from app.services.fudo_sync import FudoSyncService
    return await FudoSyncService.sync_sales(hours=hours)

@router.post("/webhook")
async def fudo_webhook(data: dict):
    """
    Endpoint para recibir notificaciones automáticas de Fudo (Webhooks).
    Cuando Fudo avisa de una nueva venta, sincronizamos los últimos 60 minutos.
    """
    print(f"📥 Webhook Fudo recibido: {data.get('action')} - {data.get('object', {}).get('id')}")
    from app.services.fudo_sync import FudoSyncService
    # Sincronizamos solo la última hora para ser rápidos
    asyncio.create_task(FudoSyncService.sync_sales(hours=1))
    return {"success": True}

@router.api_route("/sync-bills", methods=["GET", "POST"])
async def sync_fudo_bills(days: int = 7):
    """Sincroniza las facturas recientes de Fudo."""
    from app.services.fudo_sync import FudoSyncService
@router.get("/orders")
async def fetch_fudo_orders(use_db: bool = True):
    """Obtiene las ventas sincronizadas desde Supabase para el CRM."""
    from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
    import httpx
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/ventas_fudo?select=*&order=fecha_venta.desc&limit=200", 
            headers=headers
        )
        if r.status_code == 200:
            return {"success": True, "orders": r.json()}
    
    return {"success": True, "orders": []}

@router.get("/customers")
async def fetch_registered_customers():
    """Obtiene clientes registrados desde la tabla 'users' de Supabase."""
    from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
    import httpx
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    async with httpx.AsyncClient() as client:
        # Traemos usuarios ordenados por puntos (los más leales primero)
        r = await client.get(f"{SUPABASE_URL}/rest/v1/users?select=*&order=points.desc&limit=100", headers=headers)
        if r.status_code == 200:
            return {"success": True, "customers": r.json()}
    return {"success": True, "customers": []}

@router.get("/bills")
async def fetch_fudo_bills_from_db():
    """Obtiene facturas sincronizadas desde Supabase."""
    from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
    import httpx
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/facturas_fudo?select=*&order=fecha.desc&limit=100", headers=headers)
        if r.status_code == 200:
            return {"success": True, "bills": r.json()}
    return {"success": True, "bills": []}


@router.get("/buscar-boleta")
async def buscar_boleta_por_folio(
    folio: str = Query(..., description="Número de folio fiscal"),
    fecha: Optional[str] = Query(None)
):
    """Búsqueda automática vía API oficial (Sin Playwright)."""
    from app.integrations.fudo_client import FudoClient
    client = FudoClient()
    await client.refresh_token()
    
    orders = await client.fetch_orders(fecha, fecha)
    encontradas = [o for o in orders if str(o.get('number')) == folio or str(o.get('id')) == folio]
    
    return {"success": True, "ventas": encontradas, "fuente": "API Oficial Fudo"}

@router.get("/descarga-masiva")
async def descarga_masiva_fudo(
    desde: str = Query(..., description="YYYY-MM-DD"),
    hasta: str = Query(..., description="YYYY-MM-DD")
):
    """Descarga masiva automática vía API oficial."""
    from app.integrations.fudo_client import FudoClient
    client = FudoClient()
    await client.refresh_token()
    
    orders = await client.fetch_orders(desde, hasta)
    ventas_limpias = [{
        "id_fudo": o.get('id'),
        "fecha": o.get('createdAt'),
        "monto_total": o.get('total'),
        "folio_sii": o.get('number', 'Sin Folio'),
        "items": ", ".join([f"{int(i['quantity'])}x {i['name']}" for i in o.get('items', [])])
    } for o in orders]
    
    return {"success": True, "total": len(ventas_limpias), "data": ventas_limpias}
