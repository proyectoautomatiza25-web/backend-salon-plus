import requests
import os
from dotenv import load_dotenv

def find_details():
    load_dotenv()
    cid = os.getenv("FUDO_CLIENT_ID")
    sec = os.getenv("FUDO_CLIENT_SECRET")
    r_auth = requests.post("https://auth.fu.do/api", json={"apiKey": cid, "apiSecret": sec})
    token = r_auth.json().get("token")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    url = "https://api.fu.do/v1alpha1/sales"
    params = {
        "page[size]": 50,
        "filter[createdAt]": "and(gte.2026-04-08T00:00:00Z,lte.2026-04-09T23:59:59Z)"
    }
    
    r = requests.get(url, headers=headers, params=params)
    data = r.json().get("data", [])
    
    for sale in data:
        attr = sale.get("attributes", {})
        total = float(attr.get("total", 0))
        
        # El subtotal del ticket era 7.900 (después de descuento)
        if total == 7900.0 or total == 9480.0:
            print(f"Buscando detalles para Venta ID: {sale.get('id')} con Total: {total}")
            # Ver items
            items_url = f"https://api.fu.do/sales/{sale.get('id')}"
            ri = requests.get(items_url, headers=headers)
            if ri.status_code == 200:
                idat = ri.json()
                # items está en 'additions' usualmente
                additions = idat.get("additions", [])
                print(f"Items encontrados: {[a.get('name') for a in additions]}")
                # Ver si hay un number/id que diga 5982
                print(f"Venta Number: {idat.get('number')} | Identifier: {idat.get('identifier')}")
                if idat.get('number') == 5982 or "5982" in str(idat.get('identifier')):
                    print("!!! ENCONTRADA DEFINITIVAMENTE !!!")

if __name__ == "__main__":
    find_details()
