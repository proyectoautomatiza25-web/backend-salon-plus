import requests
import json
import os
from dotenv import load_dotenv

def inspect_sale_with_items():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_key = os.getenv("FUDO_CLIENT_ID")
    api_secret = os.getenv("FUDO_CLIENT_SECRET")
    
    r_auth = requests.post("https://auth.fu.do/api", json={"apiKey": api_key, "apiSecret": api_secret}, timeout=10)
    token = r_auth.json().get("token")
    
    # Intentamos traer una venta con sus items incluidos
    url = "https://api.fu.do/v1alpha1/sales"
    params = {
        "page[size]": 1,
        "include": "items"
    }
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    r = requests.get(url, headers=headers, params=params, timeout=20)
    if r.status_code == 200:
        with open("c:/Users/Lenovo/clod database/fudo_data_dump/sale_detailed_debug.json", "w", encoding="utf-8") as f:
            json.dump(r.json(), f, indent=2, ensure_ascii=False)
        print("✅ Venta detallada descargada para inspección.")

if __name__ == "__main__":
    inspect_sale_with_items()
