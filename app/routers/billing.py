from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .. import database, models, auth
import mercadopago
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/billing", tags=["Billing & Subscriptions"])

# Configurar SDK de MercadoPago
# Asegúrate de tener MP_ACCESS_TOKEN en tu archivo .env
mp_access_token = os.getenv("MP_ACCESS_TOKEN", "TEST-000000-000000-000000-000000")
sdk = mercadopago.SDK(mp_access_token)

# Mapa de precios (En producción estos deberían venir de la BD o Config)
PLAN_DETAILS = {
    'basic': {
        'reason': 'Suscripción SalonPlus Básico',
        'auto_recurring': {
            'frequency': 1,
            'frequency_type': 'months',
            'transaction_amount': 29990,
            'currency_id': 'CLP'
        }
    },
    'pro': {
        'reason': 'Suscripción SalonPlus Pro',
        'auto_recurring': {
            'frequency': 1,
            'frequency_type': 'months',
            'transaction_amount': 49990,
            'currency_id': 'CLP'
        }
    }
}

@router.post("/create-subscription")
async def create_subscription(
    plan_id: str, 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Crea una preferencia de suscripción (Preapproval) en MercadoPago y retorna el link de pago.
    """
    if plan_id not in PLAN_DETAILS:
        raise HTTPException(status_code=400, detail="Plan inválido")

    plan_data = PLAN_DETAILS[plan_id]
    
    # Construir payload para MercadoPago
    # Documentación: https://www.mercadopago.cl/developers/es/reference/subscriptions/_preapproval/post
    preapproval_data = {
        "reason": plan_data['reason'],
        "auto_recurring": plan_data['auto_recurring'],
        "payer_email": current_user.email,
        "back_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/success", # URL de retorno
        "external_reference": current_user.id, # ID del usuario para conciliar el webhook
        "status": "pending"
    }

    try:
        # Llamada a la API de MercadoPago
        # Nota: El método puede variar ligeramente según la versión del SDK, usamos la estándar.
        preference_response = sdk.preapproval().create(preapproval_data)
        
        response_json = preference_response["response"]
        
        # init_point es la URL a la que redirigimos al usuario
        init_point = response_json.get("init_point")
        
        if not init_point:
             # Fallback para sandbox/test si no devuelve init_point directo (a veces pasa en modo test)
             init_point = response_json.get("sandbox_init_point")

        return {"url": init_point, "id": response_json.get("id")}

    except Exception as e:
        print(f"Error creando suscripción MP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request, db: Session = Depends(database.get_db)):
    """
    Recibe notificaciones de MercadoPago sobre cambios en suscripciones o pagos.
    """
    try:
        # Leer body y query params
        body = await request.json()
        query_params = request.query_params
        
        topic = query_params.get("topic") or body.get("type")
        resource_id = query_params.get("id") or body.get("data", {}).get("id")

        print(f"🔔 Webhook recibido: Topic={topic}, ID={resource_id}")

        if topic == "subscription_preapproval":
            # Consultar estado actual de la suscripción en MP
            subscription_response = sdk.preapproval().get(resource_id)
            sub_data = subscription_response["response"]
            
            external_ref = sub_data.get("external_reference") # Nuestro User ID
            status_mp = sub_data.get("status") # authorized, paused, cancelled
            
            if external_ref:
                user = db.query(models.User).filter(models.User.id == external_ref).first()
                if user:
                    if status_mp == "authorized":
                        user.subscription_active = True
                        # Determinar plan basado en el monto o reason si es necesario
                        # Por simplicidad activamos suscripción genérica o actualizamos fecha
                        user.stripe_subscription_id = resource_id # Guardamos ID de MP aquí por ahora
                        print(f"✅ Suscripción ACTIVADA para usuario {user.email}")
                    
                    elif status_mp in ["cancelled", "paused"]:
                        user.subscription_active = False
                        print(f"❌ Suscripción PAUSADA/CANCELADA para usuario {user.email}")
                    
                    db.commit()

        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error en webhook: {e}")
        return {"status": "error", "detail": str(e)}
