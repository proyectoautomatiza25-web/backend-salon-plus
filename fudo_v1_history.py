import requests
import json
import os
from dotenv import load_dotenv
from datetime import date, timedelta

def get_official_fudo_token():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_key = os.getenv("FUDO_CLIENT_ID")
    api_secret = os.getenv("FUDO_CLIENT_SECRET")
    
    auth_url = "https://auth.fu.do/api"
    payload = {"apiKey": api_key, "apiSecret": api_secret}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    r = requests.post(auth_url, json=payload, headers=headers, timeout=10)
    if r.status_code == 200:
        return r.json().get("token")
    return None

def fetch_sales_range(token, start_date, end_date):
    url = "https://api.fu.do/v1alpha1/sales"
    params = {
        "page[size]": 500,
        "filter[createdAt]": f"and(gte.{start_date}T00:00:00Z,lte.{end_date}T23:59:59Z)"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    print(f"📊 Consultando ventas desde {start_date} hasta {end_date}...")
    r = requests.get(url, headers=headers, params=params, timeout=15)
    if r.status_code == 200:
        data = r.json()
        sales = data if isinstance(data, list) else data.get('data', [])
        total = sum(float(s.get('total', 0)) for s in sales)
        print(f"✅ Total recuperado: ${total} ({len(sales)} ventas)")
        return total, sales
    else:
        print(f"❌ Error: {r.status_code} - {r.text}")
        return 0, []

if __name__ == "__main__":
    token = get_official_fudo_token()
    if token:
        # Probamos todo febrero
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        total, data = fetch_sales_range(token, "2026-02-01", yesterday)
        
        with open("c:/Users/Lenovo/clod database/fudo_data_dump/real_v1_history.json", "w") as f:
            json.dump({"total": total, "count": len(data), "data": data}, f)
