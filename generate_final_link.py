import requests
import json

# TUS CREDENCIALES DE PRODUCCIÓN
ACCESS_TOKEN = "APP_USR-6703285773653661-012801-f17be76f714591ed53de2d4beeb4e6fa-3164912896"
PLAN_ID = "2f70c5201dcd4c73ba2217b4aa201950"

def create_instant_subscription(email):
    url = "https://api.mercadopago.com/preapproval"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Creamos la suscripción PENDIENTE para este email específico
    data = {
        "preapproval_plan_id": PLAN_ID,
        "payer_email": email,
        "reason": "Suscripción Salon Plus - 7 Días Gratis",
        "external_reference": f"user_{email}",
        "back_url": "https://salonplus.automatizasur.cl/success",
        "status": "pending"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        return response.json().get("init_point")
    else:
        print(f"Error: {response.text}")
        return None

# Generamos un link para una prueba real
email_test = "cliente_prueba_salon@gmail.com"
link = create_instant_subscription(email_test)

if link:
    print("\n" + "="*60)
    print("🚀 LINK GENERADO EXITOSAMENTE")
    print("="*60)
    print(f"\nEmail asignado: {email_test}")
    print(f"\nURL de pago:\n{link}")
    print("\n" + "="*60)
    print("📝 INSTRUCCIONES:")
    print("1. Abre este link en una VENTANA DE INCÓGNITO (Obligatorio)")
    print("2. NO uses tu tarjeta personal (usa otra o una de débito distinta)")
    print("3. Asegúrate de que el RUT que pongas sea válido (ej: 11.111.111-1)")
    print("="*60)
else:
    print("No se pudo generar el link.")
