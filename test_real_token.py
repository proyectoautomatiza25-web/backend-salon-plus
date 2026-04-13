import requests
import json
from datetime import datetime, timedelta

def test_token(token):
    print("🚀 Usando TOKEN extraído para Kingdom Coffee...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    # Endpoints que vimos en la captura de red
    endpoints = [
        "https://api.fu.do/sales?page=1&per_page=10",
        "https://api.fu.do/products",
        "https://api.fu.do/sale_identifiers"
    ]
    
    for url in endpoints:
        print(f"\n📡 Probando: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print("   ✅ ¡EUREKA! Datos reales obtenidos.")
                
                # Si es sales, guardar una muestra para estructurar el importador
                if "sales" in url:
                    with open("real_sales_sample.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    print("   📁 Guardada muestra en 'real_sales_sample.json'")
                    
                    # Mostrar resumen rápido
                    sales_list = data.get('data', []) if isinstance(data, dict) else data
                    if sales_list:
                        print(f"   📊 Ultima venta: {sales_list[0].get('total')} {sales_list[0].get('createdAt')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ1aSI6MzYsInVhIjp0cnVlLCJ1ciI6NSwidWwiOiJhdXRvbWF0aXphQGtpbmdkb21jb2ZmZWUiLCJhaSI6MTkxNDczLCJzaWMiOjIsImV4cCI6MTc3MDQyOTE3OX0.qZTZbPD5kMgfItgwlgacKQ5UpHxJOYa6-mplDncTiZ4"
    test_token(TOKEN)
