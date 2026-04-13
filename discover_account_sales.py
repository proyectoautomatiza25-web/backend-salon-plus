import requests
import os
from dotenv import load_dotenv

def discover_with_account_id():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    account_id = "191473" # Extraído del token
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/"
    }

    # Variaciones con el Account ID
    urls = [
        f"https://api.fu.do/accounts/{account_id}/sales",
        f"https://api.fu.do/accounts/{account_id}/daily_stats",
        f"https://api.fu.do/v2/accounts/{account_id}/sales",
        f"https://api.fu.do/sales?account_id={account_id}",
        "https://api.fu.do/sale_identifiers" # Re-check
    ]
    
    print(f"🕵️ Escaneando con ID de cuenta {account_id}...")
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"📡 {url} -> {r.status_code}")
            if r.status_code == 200:
                print(f"      ✅ ¡POSIBLE ACIERTO! {str(r.json())[:100]}")
        except:
            pass

if __name__ == "__main__":
    discover_with_account_id()
