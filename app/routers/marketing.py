from fastapi import APIRouter, HTTPException
from app.services.marketing import MarketingService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/marketing", tags=["Marketing"])


@router.post("/send-test")
@router.post("/send-test")
async def send_test_email(email: str):
    """Envía un email de prueba y devuelve el error exacto si falla."""
    try:
        success, error_msg = MarketingService.send_email(
            email,
            "☕ Kingdom Marketing Debug Test",
            "Prueba de envío."
        )
        if success:
            return {"success": True, "message": f"Email enviado a {email}. Detalle: {error_msg}"}
        else:
            return {
                "success": False, 
                "error": error_msg,
                "debug": {
                    "host": MarketingService.SMTP_HOST_STR,
                    "user": MarketingService.SMTP_USER_STR
                }
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/blast")
async def blast_campaign(campaign: dict):
    """
    Envía una campaña de email a la audiencia seleccionada.
    
    Soporta dos modos:
    1. Con `recipients`: usa la lista explícita de destinatarios enviada desde el CRM.
    2. Sin `recipients`: auto-descubre emails desde Supabase.
    """
    subject = campaign.get("subject", "Novedades en Kingdom Coffee")
    template = campaign.get("template", "welcome")
    custom_body = campaign.get("custom_body")  # Para plantilla libre
    explicit_recipients = campaign.get("recipients")  # Lista [{email, name}] desde el CRM

    # --- Modo 1: Recipients explícitos desde el CRM ---
    if explicit_recipients:
        clients_to_send = [r for r in explicit_recipients if r.get("email") and "@" in r.get("email")]
        logger.info(f"📧 Blast Campaign (explicit): {len(clients_to_send)} destinatarios, plantilla: {template}")
    else:
        # --- Modo 2: Auto-descubrimiento de emails ---
        client_dicts = []

        # b. Usuarios registrados en Supabase (App)
        from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"{SUPABASE_URL}/rest/v1/users?select=email&email=not.is.null",
                    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
                )
                if r.status_code == 200:
                    client_dicts.extend([{"email": row['email']} for row in r.json() if row.get('email')])
            except Exception as e:
                logger.warning(f"Could not query Supabase users: {e}")

            # c. Emails extraídos de ventas Fudo
            try:
                r = await client.get(
                    f"{SUPABASE_URL}/rest/v1/ventas_fudo?select=cliente_email&cliente_email=not.is.null",
                    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
                )
                if r.status_code == 200:
                    client_dicts.extend([{"email": row['cliente_email']} for row in r.json() if row.get('cliente_email')])
            except Exception as e:
                logger.warning(f"Could not query Fudo sales emails: {e}")

        # Deduplicar
        clients_to_send = list({c['email']: c for c in client_dicts if c.get('email') and '@' in c['email']}.values())
        logger.info(f"📧 Blast Campaign (auto): {len(clients_to_send)} destinatarios únicos, plantilla: {template}")

    if not clients_to_send:
        return {"success": False, "sent": 0, "message": "No se encontraron destinatarios con email válido"}

    # Usar custom_body para plantilla libre
    if template == "custom" and custom_body:
        # Inyectar el body personalizado en el servicio
        count = await MarketingService.blast_campaign(subject, "custom", clients_to_send, custom_body=custom_body)
    else:
        count = await MarketingService.blast_campaign(subject, template, clients_to_send)

    return {
        "success": count > 0,
        "sent": count,
        "total": len(clients_to_send),
        "message": f"Campaña enviada a {count} de {len(clients_to_send)} destinatarios"
    }


@router.get("/stats")
async def get_marketing_stats():
    """Estadísticas básicas del sistema de marketing."""
    from app.services.fudo_sync import SUPABASE_URL, SUPABASE_KEY
    import httpx

    stats = {"app_users": 0, "fudo_emails": 0, "total_audience": 0}

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{SUPABASE_URL}/rest/v1/users?select=email&email=not.is.null",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            )
            if r.status_code == 200:
                stats["app_users"] = len([u for u in r.json() if u.get("email")])
        except Exception:
            pass

        try:
            r = await client.get(
                f"{SUPABASE_URL}/rest/v1/ventas_fudo?select=cliente_email&cliente_email=not.is.null",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            )
            if r.status_code == 200:
                fudo_emails = list(set(row["cliente_email"] for row in r.json() if row.get("cliente_email")))
                stats["fudo_emails"] = len(fudo_emails)
        except Exception:
            pass

    stats["total_audience"] = stats["app_users"] + stats["fudo_emails"]
    return {"success": True, "stats": stats}
