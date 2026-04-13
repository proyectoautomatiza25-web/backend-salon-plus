import requests
import os
from dotenv import load_dotenv

def get_token_and_search():
    load_dotenv()
    cid = os.getenv("FUDO_CLIENT_ID")
    sec = os.getenv("FUDO_CLIENT_SECRET")
    
    auth_url = "https://auth.fu.do/api"
    p = {"apiKey": cid, "apiSecret": sec}
    r = requests.post(auth_url, json=p)
    
    if r.status_code != 200:
        print(f"Auth Fallida: {r.status_code} - {r.text}")
        return
        
    token = r.json().get("token")
    print(f"Token obtenido: {token[:10]}...")
    
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    # Probamos el endpoint de ventas CON el token
    sales_url = "https://api.fu.do/sales"
    params = {"from": "2026-04-08", "to": "2026-04-09"} # Rango mas amplio por si acaso
    
    rs = requests.get(sales_url, headers=headers, params=params)
    print(f"Sales Status: {rs.status_code}")
    
    if rs.status_code == 200:
        data = rs.json()
        items = data if isinstance(data, list) else data.get("data", [])
        print(f"Ventas encontradas: {len(items)}")
        
        for sale in items:
            number = sale.get("number")
            total = sale.get("total")
            if str(number) == "5982":
                print(f"!!! BINGO !!!")
                print(f"Encontrada Venta #5982")
                print(f"Monto Total: ${total}")
                print(f"Fecha: {sale.get('createdAt')}")
                return
        
        print("No se encontro el numero 5982 entre las ventas listadas.")
        print(f"Numeros en lista: {[s.get('number') for s in items[:15]]}")

if __name__ == "__main__":
    get_token_and_search()
