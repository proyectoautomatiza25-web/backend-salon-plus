import requests
import os
import json
from datetime import datetime

class SubscriptionService:
    def __init__(self):
        self.access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896")
        self.plan_id = os.getenv("MP_PLAN_ID", "f68137a2c5e5445e974e291c6d4b0a71")

    def create_subscription_link(self, email):
        """
        Crea un link de pre-aprobación (suscripción) usando la API REST directa.
        """
        url = "https://api.mercadopago.com/preapproval"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "preapproval_plan_id": self.plan_id,
            "payer_email": email,
            "back_url": "https://salonplus.automatizasur.cl/subscription-success",
            "status": "pending"
        }

        try:
            print(f"DEBUG: Intentando crear suscripción para {email} con plan {self.plan_id}")
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()
            
            if response.status_code == 201:
                checkout_url = result.get("init_point")
                print(f"DEBUG: Link creado exitosamente: {checkout_url}")
                return checkout_url
            else:
                print(f"DEBUG: Error de Mercado Pago ({response.status_code}): {result}")
                return None
        except Exception as e:
            print(f"DEBUG: Excepción al conectar con Mercado Pago: {e}")
            return None

subscription_service = SubscriptionService()
