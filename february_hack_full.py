import requests
import json
import os
from dotenv import load_dotenv
from datetime import date, timedelta

def hack_full_february():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    today = date.today()
    start_date = "2026-02-01"
    end_date = today.isoformat()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "fudo-country-code": "CL"
    }

    url = f"https://api.fu.do/sales?from={start_date}&to={end_date}&per_page=100"
    
    print(f"🕵️‍♂️ Hackeando TODO FEBRERO ({start_date} al {end_date})...")
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            data = r.json()
            items = data.get('data', data)
            if isinstance(items, dict): items = list(items.values())
            
            # Procesar por dia para el grafico
            daily_totals = {}
            grand_total = 0
            for sale in items:
                day = sale.get('createdAt', '2026-02-01')[:10]
                amount = float(sale.get('amount', 0))
                daily_totals[day] = daily_totals.get(day, 0) + amount
                grand_total += amount
                
            print(f"✅ ¡HACK COMPLETADO! Se encontraron ventas en {len(daily_totals)} dias.")
            print(f"💰 DINERO TOTAL FEBRERO: ${grand_total}")
            
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/february_real_sales.json", "w") as f:
                json.dump({"total": grand_total, "daily": daily_totals, "raw_count": len(items)}, f)
            return True
        else:
            print(f"❌ Error {r.status_code}")
    except Exception as e:
        print(f"💥 Error: {e}")
            
    return False

if __name__ == "__main__":
    hack_full_february()
