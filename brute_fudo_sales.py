import requests
import os
from dotenv import load_dotenv
import json

def brute_force_fudo_sales():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Posibles variaciones del endpoint de ventas en v2
    patterns = [
        "https://api.fu.do/sales",
        "https://api.fu.do/v2/sales",
        "https://api.fu.do/sales/search",
        "https://api.fu.do/orders",
        "https://api.fu.do/v2/orders",
        "https://api.fu.do/restaurant/sales",
        "https://api.fu.do/sale_reports"
    ]
    
    print("🎯 Intentando forzar el acceso a las VENTAS...")
    for url in patterns:
        try:
            # Probamos con parametros de fecha para que no de error por "demasiados datos"
            r = requests.get(f"{url}?per_page=1", headers=headers, timeout=5)
            print(f"📡 {url} -> {r.status_code}")
            if r.status_code == 200:
                print(f"      ✅ ¡ESTE ES! Link encontrado.")
                with open("working_sales_url.txt", "w") as f:
                    f.write(url)
                return url
        except:
            pass
    return None

if __name__ == "__main__":
    brute_force_fudo_sales()
