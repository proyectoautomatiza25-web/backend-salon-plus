import requests
import os
from dotenv import load_dotenv

def find_exact_receipt():
    load_dotenv()
    cid = os.getenv("FUDO_CLIENT_ID")
    sec = os.getenv("FUDO_CLIENT_SECRET")
    r_auth = requests.post("https://auth.fu.do/api", json={"apiKey": cid, "apiSecret": sec})
    token = r_auth.json().get("token")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    # Buscamos exactamente el 8 de Abril
    # La API v1alpha1 usa filtros de fecha
    url = "https://api.fu.do/v1alpha1/sales"
    params = {
        "page[size]": 100,
        "filter[createdAt]": "and(gte.2026-04-08T00:00:00Z,lte.2026-04-08T23:59:59Z)"
    }
    
    r = requests.get(url, headers=headers, params=params)
    data = r.json().get("data", [])
    print(f"Encontradas {len(data)} ventas el dia 8 de Abril.")
    
    for sale in data:
        attr = sale.get("attributes", {})
        total = float(attr.get("total", 0))
        # En la foto el subtotal es 7.900 despues de descuento
        # Fudo a veces guarda el Subtotal o el Total. 
        if total == 7900.0 or total == 9480.0 or total == 15800.0:
            print(f"POSIBLE MATCH: ID {sale.get('id')} | Total: ${total} | Hora: {attr.get('createdAt')}")
            # Intentar ver el id corto (number)
            # En v1alpha1 a veces viene en 'number'
            if attr.get("number") == 5982:
                print("!!! MATCH BRUTAL ENCONTRADO !!!")
                return

if __name__ == "__main__":
    find_exact_receipt()
