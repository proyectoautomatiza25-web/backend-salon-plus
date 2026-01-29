import mercadopago
import json

ACCESS_TOKEN = "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896"
PLAN_ID = "f9f6fb0ec30d41ecbe6b18ea75f8ecd9"

sdk = mercadopago.SDK(ACCESS_TOKEN)

# Payload mínimo para ver si obtenemos init_point sin card_token
preapproval_data = {
    "preapproval_plan_id": PLAN_ID,
    "payer_email": "test_service_user@test.com",
    "back_url": "https://salonplus.automatizasur.cl/subscription-success",
    "external_reference": "test-user-id"
}

print("Prueba 2: Sin status...")
response = sdk.preapproval().create(preapproval_data)
print("Status Code:", response["status"])
print("Response Body:", json.dumps(response["response"], indent=4))
