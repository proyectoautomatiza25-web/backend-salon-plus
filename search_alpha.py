import requests
import os
from dotenv import load_dotenv

def search_v1alpha1():
    load_dotenv()
    cid = os.getenv("FUDO_CLIENT_ID")
    sec = os.getenv("FUDO_CLIENT_SECRET")
    
    # Auth
    r_auth = requests.post("https://auth.fu.do/api", json={"apiKey": cid, "apiSecret": sec})
    token = r_auth.json().get("token")
    
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    # Usamos el endpoint v1alpha1 que está en sync_official.py
    url = "https://api.fu.do/v1alpha1/sales"
    params = {
        "page[size]": 100,
        "filter[createdAt]": "and(gte.2026-04-01T00:00:00Z,lte.2026-04-09T23:59:59Z)"
    }
    
    print(f"Buscando en {url}...")
    r = requests.get(url, headers=headers, params=params)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json().get("data", [])
        print(f"Ventas en v1alpha1: {len(data)}")
        for sale in data:
            attr = sale.get("attributes", {})
            num = attr.get("number")
            total = attr.get("total")
            print(f" - #{num}: ${total}")
            if str(num) == "5982":
                print("!!! ENCONTRADA EN V1ALPHA1 !!!")
                return
    else:
        print(r.text)

if __name__ == "__main__":
    search_v1alpha1()
