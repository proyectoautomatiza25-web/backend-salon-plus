import httpx
import os
import logging
import asyncio
from datetime import date, datetime, timedelta
from app.integrations.fudo_client import FudoClient

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "https://bcfulknkkwlpxpiuboyt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("VITE_SUPABASE_ANON_KEY"))

class FudoSyncService:
    @staticmethod
    async def sync_menu():
        """Extrae el menú completo de Fudo y lo guarda en Supabase vía Bulk Insert."""
        print("Iniciando extraccion de menu desde Fudo...")
        client = FudoClient()
        products = await client.fetch_products()
        
        if not products:
            print("❌ No se pudieron obtener productos de Fudo.")
            return {"success": False, "message": "No se obtuvieron productos de Fudo"}

        print(f"✅ Se obtuvieron {len(products)} productos. Sincronizando con Supabase...")

        # Preparar headers para Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

        # Normalizar objetos para Supabase
        items_to_sync = []
        for p in products:
            # FILTRO: Solo productos que deberían estar en el menú público
            # Fudo usa enableOnlineMenu o enableQrMenu
            is_visible = p.get("enableOnlineMenu", False) or p.get("enableQrMenu", False)
            
            # También ignoramos productos sin nombre o sin ID
            if not is_visible or not p.get("id"):
                continue

            # Mapeo a columnas reales en Supabase (en español)
            # Schema: id (int), nombre (text), precio (numeric), categoria (text), imagen_url (text), disponible (bool)
            item = {
                "id": int(p.get("id")),
                "nombre": p.get("name") or p.get("nombre"),
                "precio": float(p.get("price") or p.get("precio") or 0),
                "categoria": str(p.get("productCategoryId") or p.get("categoryId") or ""),
                "imagen_url": p.get("imageUrl") or p.get("image_url") or "",
                "disponible": True
            }
            items_to_sync.append(item)

        if not items_to_sync:
            return {"success": True, "synced": 0, "message": "No se encontraron productos visibles para el menú."}

        try:
            # Añadimos header para UPSERT (update si existe el ID)
            headers["Prefer"] = "resolution=merge-duplicates"
            
            async with httpx.AsyncClient(timeout=30.0) as sb_client:
                # PostgREST bulk upsert: enviamos la lista completa con on_conflict=id
                r = await sb_client.post(
                    f"{SUPABASE_URL}/rest/v1/productos_fudo?on_conflict=id",
                    json=items_to_sync,
                    headers=headers
                )
                if r.status_code in [200, 201, 204]:
                    print(f"✨ Sincronización de menú finalizada: {len(items_to_sync)} productos.")
                    return {"success": True, "synced": len(items_to_sync)}
                else:
                    logger.error(f"Error bulk sync menu: {r.text}")
                    return {"success": False, "message": r.text}
        except Exception as e:
            logger.error(f"Exception bulk sync menu: {e}")
            return {"success": False, "message": str(e)}

    @staticmethod
    async def sync_sales(hours=24):
        """Extrae las ventas de las últimas N horas de Fudo de forma optimizada para Vercel."""
        print(f"Sincronizando ventas de las ultimas {hours} horas...")
        client = FudoClient()
        await client.refresh_token()

        # 1. Obtener lista de IDs de ventas en el período
        now_utc = datetime.utcnow()
        desde = now_utc - timedelta(hours=int(hours))
        hasta = now_utc + timedelta(hours=24) 
        
        raw_sales = await client.fetch_orders(desde, hasta)
        if not raw_sales:
            logger.info("Fudo /sales con filtros vacío, probando fallback /sale_identifiers")
            raw_sales = await client.fetch_orders(None, None)
            
        if not raw_sales:
            return {"success": True, "synced": 0, "message": "No hay nuevas ventas en Fudo."}

        all_ids = []
        for s in raw_sales:
            sid = str(s.get('id')) if isinstance(s, dict) else str(s)
            if sid: all_ids.append(sid)

        if not all_ids:
            return {"success": True, "synced": 0}

        # 2. Consultar Supabase para evitar duplicados innecesarios (OPCIONAL pero bueno para performance)
        headers = {
            "apikey": SUPABASE_KEY, 
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        # 3. Procesar bloque de ventas
        # Limitamos a 50 para evitar timeouts en Vercel
        batch = raw_sales[:50]
        auth_headers = client.get_auth_headers()

        async def process_single_sale(s, http_client):
            sale_id = str(s.get('id')) if isinstance(s, dict) else str(s)
            try:
                sr = await http_client.get(f"{client.base_url}/sales/{sale_id}", headers=auth_headers)
                if sr.status_code != 200: return None
                sale_data = sr.json()

                telefono_wa = None
                cliente_email = None
                gid = sale_data.get('guestId')
                
                if gid:
                    gr = await http_client.get(f"{client.base_url}/guests/{gid}", headers=auth_headers)
                    if gr.status_code == 200:
                        guest = gr.json()
                        cliente_email = guest.get('email')
                        raw_phones = [guest.get('phone'), guest.get('mobile'), guest.get('description')]
                        for rp in raw_phones:
                            if not rp: continue
                            digits = "".join(filter(str.isdigit, str(rp)))
                            if len(digits) >= 8:
                                # Normalización simple para Chile
                                if digits.startswith("56") and len(digits) == 11:
                                    telefono_wa = digits
                                elif digits.startswith("9") and len(digits) == 9:
                                    telefono_wa = "56" + digits
                                break
                
                # Check customer field as fallback
                cust = sale_data.get('customer')
                if cust:
                    cliente_email = cliente_email or cust.get('email')
                    telefono_wa = telefono_wa or cust.get('phone')

                return (sale_data, telefono_wa, cliente_email)
            except:
                return None

        async with httpx.AsyncClient(timeout=10.0) as http_client:
            tasks = [process_single_sale(s, http_client) for s in batch]
            results = await asyncio.gather(*tasks)

        # 4. Preparar payload para Supabase
        sales_to_sync = []
        for res in results:
            if not res: continue
            s, tel, mail = res
            
            # Calcular total y conceptos
            items = s.get('additions') or []
            conceptos_list = []
            total = 0
            for it in items:
                if not it.get('cancellationComment'):
                    qty = float(it.get('count', 1))
                    pr = float(it.get('price', 0))
                    total += pr * qty
                    conceptos_list.append(f"{int(qty)}x {it.get('name')}")
            
            # Backup total si additions fallan
            if total == 0:
                total = sum(float(p.get('amount', 0)) for p in s.get('payments', []) if not p.get('canceled'))

            # Dualidad Inteligente: ID Técnico para el sistema, Número de Ticket para el Cliente
            fudo_tech_id = str(s.get('id', ''))
            ticket_number = str(s.get('number', ''))

            sales_to_sync.append({
                "fudo_order_id": fudo_tech_id, # Llave técnica única
                "folio_sii": ticket_number,     # El número que el cliente ve (ej: 5982)
                "monto_total": total,
                "cliente_telefono": tel,
                "cliente_email": mail,
                "puntos_generados": int(total / 10000),
                "conceptos": ", ".join(conceptos_list)[:250] if conceptos_list else "Consumo Kingdom",
                "fecha_venta": s.get('createdAt') or datetime.utcnow().isoformat()
            })

        if not sales_to_sync:
            return {"success": True, "synced": 0}

        # 5. Bulk Upsert a Supabase
        async with httpx.AsyncClient() as sb_client:
            r = await sb_client.post(
                f"{SUPABASE_URL}/rest/v1/ventas_fudo?on_conflict=fudo_order_id",
                json=sales_to_sync,
                headers=headers
            )
            
            if r.status_code in [200, 201, 204]:
                print(f"✅ Sincronizadas {len(sales_to_sync)} ventas.")
                return {"success": True, "synced": len(sales_to_sync)}
            else:
                # Fallback: Quitar columnas que tal vez no existan (legacy fix)
                logger.warning(f"Error en primer intento de sync sales: {r.text}. Reintentando sin campos extra...")
                for s in sales_to_sync:
                    s.pop("conceptos", None)
                    s.pop("cliente_email", None)
                    s.pop("folio_sii", None) # Fallback por si la columna no existe aún
                
                r2 = await sb_client.post(
                    f"{SUPABASE_URL}/rest/v1/ventas_fudo?on_conflict=fudo_order_id",
                    json=sales_to_sync,
                    headers=headers
                )
                return {"success": r2.status_code in [200, 201, 204], "synced": len(sales_to_sync) if r2.status_code < 300 else 0}

    @staticmethod
    async def sync_bills(days=7):
        """Sincroniza facturas y boletas electrónicas."""
        print(f"📄 Sincronizando facturas de los últimos {days} días...")
        client = FudoClient()
        now = datetime.now()
        desde = (now - timedelta(days=days)).date()
        hasta = (now + timedelta(days=1)).date()
        
        bills = await client.fetch_bills(desde, hasta)
        if not bills:
            return {"success": True, "synced": 0}

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

        bills_to_sync = []
        for b in bills:
            bills_to_sync.append({
                "fudo_bill_id": str(b.get('id')),
                "tipo": b.get('type'),
                "numero": b.get('number'),
                "monto": float(b.get('total', 0)),
                "fecha": b.get('createdAt'),
                "cliente_nombre": b.get('client', {}).get('name') if b.get('client') else None,
                "sale_id": str(b.get('saleId')) if b.get('saleId') else None
            })

        if not bills_to_sync:
            return {"success": True, "synced": 0}

        async with httpx.AsyncClient() as sb_client:
            r = await sb_client.post(
                f"{SUPABASE_URL}/rest/v1/facturas_fudo?on_conflict=fudo_bill_id",
                json=bills_to_sync,
                headers=headers
            )
            return {"success": r.status_code in [200, 201, 204], "synced": len(bills_to_sync)}
