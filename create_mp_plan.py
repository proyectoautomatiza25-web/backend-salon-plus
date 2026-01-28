import mercadopago
import json

# Tus credenciales de TEST
ACCESS_TOKEN = "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896"
sdk = mercadopago.SDK(ACCESS_TOKEN)

def create_plan():
    plan_data = {
        "reason": "Plan Pro Salon Plus (Prueba 7 días)",
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
        "back_url": "https://salonplus.automatizasur.cl/subscription-success"
    }

    result = sdk.preapproval_plan().create(plan_data)
    print(json.dumps(result["response"], indent=4))

if __name__ == "__main__":
    create_plan()
