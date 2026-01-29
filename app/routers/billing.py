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
    Crea una suscripción vinculada al plan configurado.
    """
    if not mp_plan_id:
        raise HTTPException(status_code=500, detail="MP_PLAN_ID no configurado")

    preapproval_data = {
        "preapproval_plan_id": mp_plan_id,
        "payer_email": current_user.email,
        "back_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/subscription-success",
        "external_reference": current_user.id,
        "status": "pending"
    }

    try:
        preference_response = sdk.preapproval().create(preapproval_data)
        response_json = preference_response["response"]
        
        init_point = response_json.get("init_point") or response_json.get("sandbox_init_point")
        
        return {"url": init_point, "id": response_json.get("id")}

    except Exception as e:
        print(f"Error creando suscripción MP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
            status_mp = sub_data.get("status")
            
            if external_ref:
                user = db.query(models.User).filter(models.User.id == external_ref).first()
                if user:
                    if status_mp == "authorized":
                        user.subscription_active = True
                        user.plan_type = "pro"
                        user.stripe_subscription_id = resource_id # Usamos column existente por ahora
                        print(f"✅ Suscripción ACTIVADA para usuario {user.email}")
                    
                    elif status_mp in ["cancelled", "paused"]:
                        user.subscription_active = False
                        print(f"❌ Suscripción PAUSADA/CANCELADA para usuario {user.email}")
                    
                    db.commit()

        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error en webhook: {e}")
        return {"status": "error", "detail": str(e)}
