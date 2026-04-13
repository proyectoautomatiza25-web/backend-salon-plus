import requests
import os
from dotenv import load_dotenv

def probe_sales_with_origin():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    # Algunas APIs bloquean si no ven que vienes de su propia web
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Probamos el endpoint de ventas CON los headers de navegacion
    url = "https://api.fu.do/sales?per_page=10"
    print(f"🚀 Probando ventas con headers de navegación en {url}...")
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ ¡BINGO! Las ventas ya fluyen.")
            return True
        else:
            print(f"❌ Sigue bloqueado: {r.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

if __name__ == "__main__":
    probe_sales_with_origin()
