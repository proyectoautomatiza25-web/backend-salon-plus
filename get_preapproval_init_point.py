import requests
import json

ACCESS_TOKEN = "APP_USR-6703285773653661-012801-f17be76f714591ed53de2d4beeb4e6fa-3164912896"
PLAN_ID = "2f70c5201dcd4c73ba2217b4aa201950"

# Intentar crear una pre-suscripcion para obtener un init_point nuevo
data = {
    "preapproval_plan_id": PLAN_ID,
    "payer_email": "comprador_test@tu-dominio.com",
    "back_url": "https://salonplus.automatizasur.cl/subscription-success",
    "reason": "Plan Pro Salon Plus",
    "external_reference": "user_id_123",
    "status": "pending"
}

url = "https://api.mercadopago.com/preapproval"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code in [200, 201]:
    res_data = response.json()
    print(f"Init Point: {res_data.get('init_point')}")
else:
    print(f"Error {response.status_code}: {response.text}")
