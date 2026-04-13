import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def payment_daily_breakdown():
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
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            sales = data.get('data', data)
            if isinstance(sales, dict): sales = list(sales.values())
            
            daily_stats = {}
            grand_total = 0
            
            for s in sales:
                day = s.get('createdAt', '2026-02-01')[:10]
                payments = s.get('payments', [])
                day_total = 0
                for p in payments:
                    if not p.get('canceled'):
                        day_total += float(p.get('amount', 0))
                
                daily_stats[day] = daily_stats.get(day, 0) + day_total
                grand_total += day_total
            
            # Ordenar por fecha
            sorted_days = sorted(daily_stats.keys())
            chart_data = {
                "labels": sorted_days,
                "values": [daily_stats[d] for d in sorted_days],
                "total": grand_total
            }
            
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/real_daily_revenue.json", "w") as f:
                json.dump(chart_data, f)
            print(f"✅ Desglose real generado: {len(sorted_days)} días con ventas.")
            return True
    except: pass
    return False

if __name__ == "__main__":
    payment_daily_breakdown()
