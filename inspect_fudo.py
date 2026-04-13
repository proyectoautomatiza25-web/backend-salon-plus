import requests
import json

def inspect_fudo_session(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    url = "https://api.fu.do/sale_identifiers"
    print(f"Inspeccionando Fudo: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Respuesta (primeros 500 chars): {str(data)[:500]}")
            # Si data es una lista de IDs, probaremos pedir una venta
            if isinstance(data, list) and len(data) > 0:
                first_id = data[0]
                print(f"\nProbando obtener detalle de venta {first_id}...")
                r_detail = requests.get(f"https://api.fu.do/sales/{first_id}", headers=headers)
                print(f"Status Detalle: {r_detail.status_code}")
                if r_detail.status_code == 200:
                    print(f"Detalle: {str(r_detail.json())[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ1aSI6MzYsInVhIjp0cnVlLCJ1ciI6NSwidWwiOiJhdXRvbWF0aXphQGtpbmdkb21jb2ZmZWUiLCJhaSI6MTkxNDczLCJzaWMiOjIsImV4cCI6MTc3MDQyOTE3OX0.qZTZbPD5kMgfItgwlgacKQ5UpHxJOYa6-mplDncTiZ4"
    inspect_fudo_session(TOKEN)
