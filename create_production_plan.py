import requests
import json

# Credenciales de PRODUCCIÓN
ACCESS_TOKEN = "APP_USR-6703285773653661-012801-f17be76f714591ed53de2d4beeb4e6fa-3164912896"

# Configuración del plan REAL
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

print("Creando plan de PRODUCCION...")
print(f"Configuracion:")
print(f"   - Precio: $29.990 CLP/mes")
print(f"   - Trial: 7 dias GRATIS")
print(f"   - Cobro automatico despues del trial")
print()

response = requests.post(url, headers=headers, json=plan_data)

print(f"Status Code: {response.status_code}")
print()

if response.status_code in [200, 201]:
    result = response.json()
    print("Plan de PRODUCCION creado exitosamente!")
    print()
    print(f"Plan ID: {result['id']}")
    print(f"Nombre: {result['reason']}")
    print(f"Precio: ${result['auto_recurring']['transaction_amount']:,} CLP/mes")
    print(f"Trial: {result['auto_recurring']['free_trial']['frequency']} dias gratis")
    print()
    print(f"Link de checkout:")
    print(f"https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id={result['id']}")
    print()
    print("=" * 80)
    print("IMPORTANTE: Este es un plan de PRODUCCION")
    print("   - Los pagos seran REALES")
    print("   - Usa tarjetas reales para probar")
    print("   - Puedes cancelar la suscripcion inmediatamente despues de probar")
    print("=" * 80)
    print()
    print(f"Actualiza el codigo con: MP_PLAN_ID = '{result['id']}'")
    print(f"Y: MP_ACCESS_TOKEN = '{ACCESS_TOKEN}'")
else:
    print("Error creando el plan:")
    print(response.text)
