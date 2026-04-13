import requests
import os
from dotenv import load_dotenv

def find_details_v2():
    load_dotenv()
    cid = os.getenv("FUDO_CLIENT_ID")
    sec = os.getenv("FUDO_CLIENT_SECRET")
    r_auth = requests.post("https://auth.fu.do/api", json={"apiKey": cid, "apiSecret": sec})
    token = r_auth.json().get("token")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    # Traemos 200 ventas de todo abril
    url = "https://api.fu.do/v1alpha1/sales"
    params = {
        "page[size]": 200,
        "filter[createdAt]": "and(gte.2026-04-01T00:00:00Z,lte.2026-04-10T23:59:59Z)"
    }
    
    r = requests.get(url, headers=headers, params=params)
    data = r.json().get("data", [])
    print(f"Buscando en {len(data)} ventas...")
    
    for sale in data:
        attr = sale.get("attributes", {})
        total = float(attr.get("total", 0))
        
        # Filtramos por el monto de la foto ($7.900 subtotal boleta o $9.480 total con propina)
        if total == 7900.0 or total == 9480.0:
            print(f"--- CANDIDATA ENCONTRADA ---")
            print(f"ID: {sale.get('id')} | Total: {total} | Fecha: {attr.get('createdAt')}")
            
            # Ver detalle extendido
            ri = requests.get(f"https://api.fu.do/sales/{sale.get('id')}", headers=headers)
            if ri.status_code == 200:
                idat = ri.json()
                items = idat.get("additions", [])
                print(f"Items: {[i.get('name') for i in items]}")
                print(f"Daily Identifier (number): {idat.get('number')}")
                if str(idat.get('number')) == "5982":
                    print("!!! ESTA ES LA BOLETA DE LA FOTO !!!")
                    print("PRUEBA LOGRADA: EL SISTEMA PUEDE IDENTIFICAR LA BOLETA POR ID Y MONTO.")

if __name__ == "__main__":
    find_details_v2()
