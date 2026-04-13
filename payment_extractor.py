import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def payment_brute_extractor():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    today = date.today().isoformat()
    start_feb = "2026-02-01"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }

    url = f"https://api.fu.do/sales?from={start_feb}&to={today}&per_page=100"
    
    print("🎣 Extrayendo cada CENTAVO de los pagos de Febrero...")
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            sales = data.get('data', data)
            if isinstance(sales, dict): sales = list(sales.values())
            
            real_money = 0
            count = 0
            for s in sales:
                payments = s.get('payments', [])
                for p in payments:
                    amount = float(p.get('amount', 0))
                    if not p.get('canceled'):
                        real_money += amount
                        count += 1
            
            print(f"✅ ¡BOTÍN CALCULADO! Total real en pagos: ${real_money} ({count} transacciones)")
            
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/real_payment_calc.json", "w") as f:
                json.dump({"total": real_money, "transacciones": count}, f)
            return real_money
    except: pass
    return 0

if __name__ == "__main__":
    payment_brute_extractor()
