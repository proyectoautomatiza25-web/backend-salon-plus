import requests
import json

ACCESS_TOKEN = "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896"

def create_plan():
    url = "https://api.mercadopago.com/preapproval_plan"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    plan_data = {
        "reason": "Plan Pro Salon Plus (7 días Gratis)",
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

    response = requests.post(url, headers=headers, data=json.dumps(plan_data))
    print(json.dumps(response.json(), indent=4))

if __name__ == "__main__":
    create_plan()
