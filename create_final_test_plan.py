import requests
import json

# VOLVEMOS A CREDENCIALES DE PRUEBA PARA NO USAR DINERO REAL
ACCESS_TOKEN = "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896"

plan_data = {
    "reason": "TEST Plan Pro Salon Plus (Sin Trial para activar boton)",
    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 29990,
        "currency_id": "CLP"
        # SIN free_trial para que el botón se active
    },
    "back_url": "https://salonplus.automatizasur.cl/subscription-success",
    "payment_methods_allowed": {
        "payment_types": [{"id": "credit_card"}],
        "payment_methods": [{"id": "master"}, {"id": "visa"}]
    }
}

url = "https://api.mercadopago.com/preapproval_plan"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("Creando plan de PRUEBAS sin trial...")
response = requests.post(url, headers=headers, json=plan_data)

if response.status_code in [200, 201]:
    result = response.json()
    plan_id = result['id']
    print(f"✅ EXITOSO!")
    print(f"NUEVO PLAN TEST ID: {plan_id}")
    print(f"URL: https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id={plan_id}")
    
    with open('FINAL_TEST_PLAN_ID.txt', 'w') as f:
        f.write(plan_id)
else:
    print(f"Error: {response.text}")
