import requests
import json

ACCESS_TOKEN = "APP_USR-6703285773653661-012801-f17be76f714591ed53de2d4beeb4e6fa-3164912896"

plan_data = {
    "reason": "Plan Pro Salon Plus",
    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 29990,
        "currency_id": "CLP",
        "free_trial": {
            "frequency": 7,
            "frequency_type": "days"
        }
    },
    "back_url": "https://salonplus.automatizasur.cl/subscription-success",
    "payment_methods_allowed": {
        "payment_types": [{"id": "credit_card"}],
        "payment_methods": [{"id": "master"}, {"id": "visa"}, {"id": "amex"}]
    }
}

url = "https://api.mercadopago.com/preapproval_plan"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=plan_data)

if response.status_code in [200, 201]:
    result = response.json()
    plan_id = result['id']
    
    # Guardar en archivo
    with open('PRODUCTION_PLAN_ID.txt', 'w') as f:
        f.write(f"PLAN_ID={plan_id}\n")
        f.write(f"ACCESS_TOKEN={ACCESS_TOKEN}\n")
        f.write(f"\nCheckout URL:\n")
        f.write(f"https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id={plan_id}\n")
    
    print(f"Plan ID: {plan_id}")
    print(f"Guardado en: PRODUCTION_PLAN_ID.txt")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
