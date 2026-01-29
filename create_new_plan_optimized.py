import requests
import json

# Credenciales de TEST
ACCESS_TOKEN = "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896"

# Configuración del nuevo plan (sin validación de tarjeta previa)
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
        "payment_methods": [{"id": "master"}, {"id": "visa"}]
    }
}

url = "https://api.mercadopago.com/preapproval_plan"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("🔄 Creando nuevo plan optimizado para testing...")
print(f"📋 Configuración: {json.dumps(plan_data, indent=2)}")
print()

response = requests.post(url, headers=headers, json=plan_data)

print(f"📊 Status Code: {response.status_code}")
print()

if response.status_code in [200, 201]:
    result = response.json()
    print("✅ ¡Plan creado exitosamente!")
    print()
    print(f"🆔 Plan ID: {result['id']}")
    print(f"📝 Nombre: {result['reason']}")
    print(f"💰 Precio: ${result['auto_recurring']['transaction_amount']:,} CLP/mes")
    print(f"🎁 Trial: {result['auto_recurring']['free_trial']['frequency']} días gratis")
    print()
    print(f"🔗 Link de checkout:")
    print(f"https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id={result['id']}")
    print()
    print("=" * 60)
    print("IMPORTANTE: Actualiza este Plan ID en el código:")
    print(f"MP_PLAN_ID = '{result['id']}'")
    print("=" * 60)
else:
    print("❌ Error creando el plan:")
    print(response.text)
