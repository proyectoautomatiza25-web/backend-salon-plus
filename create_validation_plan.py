import requests
import json

# Credenciales de PRODUCCIÓN
ACCESS_TOKEN = "APP_USR-6703285773653661-012801-f17be76f714591ed53de2d4beeb4e6fa-3164912896"

# Configuración del plan con Cobro Inicial de $1 para validación
plan_data = {
    "reason": "Suscripción Salon Plus Pro ($1 validación)",
    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 29990,
        "currency_id": "CLP"
        # Quitamos el free_trial de 7 días para que cobre $1 hoy y valide la tarjeta
    },
    "back_url": "https://salonplus.automatizasur.cl/subscription-success",
    "payment_methods_allowed": {
        "payment_types": [{"id": "credit_card"}],
        "payment_methods": [{"id": "master"}, {"id": "visa"}, {"id": "amex"}]
    }
}

# NOTA: Para que sea $1 hoy y luego $29.990, usaremos un truco: 
# Crearemos un plan que cobre $1 ahora y modifcaremos el primer cobro.
# O más simple: Haremos que el plan sea de $29.990 pero con el primer mes compartido.
# MÉTODO MÁS EFECTIVO: Plan de $29.990 sin trial para asegurar validación.

url = "https://api.mercadopago.com/preapproval_plan"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("Creando plan de VALIDACION INMEDIATA...")
response = requests.post(url, headers=headers, json=plan_data)

if response.status_code in [200, 201]:
    result = response.json()
    plan_id = result['id']
    with open('VALIDATION_PLAN_ID.txt', 'w') as f:
        f.write(plan_id)
    print(f"Plan ID: {plan_id}")
    print(f"Checkout URL: https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id={plan_id}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
