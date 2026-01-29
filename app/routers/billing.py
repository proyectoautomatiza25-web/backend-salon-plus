from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .. import database, models, auth
import mercadopago
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/billing", tags=["Billing & Subscriptions"])

# Configurar SDK de MercadoPago
mp_access_token = os.getenv("MP_ACCESS_TOKEN", "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896")
mp_plan_id = os.getenv("MP_PLAN_ID", "f9f6fb0ec30d41ecbe6b18ea75f8ecd9")
sdk = mercadopago.SDK(mp_access_token)

@router.post("/create-subscription")
async def create_subscription(
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retorna el link directo de suscripción al plan de Mercado Pago.
    """
    if not mp_plan_id:
        raise HTTPException(status_code=500, detail="MP_PLAN_ID no configurado")

    # Usamos el link directo del checkout del plan. 
    # Mercado Pago permite pasar external_reference en la URL para algunos tipos de checkout.
    # Si no, usaremos el email para conciliar en el webhook.
    checkout_url = f"https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id={mp_plan_id}&external_reference={current_user.id}"
    
    # También podemos pre-cargar el email del pagador si el checkout lo soporta
    checkout_url += f"&payer_email={current_user.email}"

    return {"url": checkout_url}

@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request, db: Session = Depends(database.get_db)):
    """
    Recibe notificaciones de MercadoPago.
    """
    try:
        body = await request.json()
        topic = body.get("type") or request.query_params.get("topic")
        resource_id = body.get("data", {}).get("id") or request.query_params.get("id")

        print(f"🔔 Webhook recibido: Topic={topic}, ID={resource_id}")

        if topic in ["subscription_preapproval", "preapproval"]:
            # Consultar estado actual
            subscription_response = sdk.preapproval().get(resource_id)
            sub_data = subscription_response["response"]
            
            external_ref = sub_data.get("external_reference")
            payer_email = sub_data.get("payer_email")
            status_mp = sub_data.get("status")
            
            user = None
            if external_ref:
                user = db.query(models.User).filter(models.User.id == external_ref).first()
            
            if not user and payer_email:
                user = db.query(models.User).filter(models.User.email == payer_email).first()

            if user:
                if status_mp == "authorized":
                    user.subscription_active = True
                    user.plan_type = "pro"
                    user.stripe_subscription_id = resource_id
                    print(f"✅ Suscripción ACTIVADA para usuario {user.email}")
                
                elif status_mp in ["cancelled", "paused"]:
                    user.subscription_active = False
                    print(f"❌ Suscripción PAUSADA/CANCELADA para usuario {user.email}")
                
                db.commit()

        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error en webhook: {e}")
        return {"status": "error", "detail": str(e)}
