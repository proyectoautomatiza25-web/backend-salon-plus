import requests
import json
import os
from dotenv import load_dotenv
from datetime import date, timedelta

def get_official_fudo_token():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_key = os.getenv("FUDO_CLIENT_ID")
    api_secret = os.getenv("FUDO_CLIENT_SECRET")
    auth_url = "https://auth.fu.do/api"
    payload = {"apiKey": api_key, "apiSecret": api_secret}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    r = requests.post(auth_url, json=payload, headers=headers, timeout=10)
    return r.json().get("token") if r.status_code == 200 else None

def sync_all_official_data():
    token = get_official_fudo_token()
    if not token: return
    
    today = date.today().isoformat()
    start_feb = "2026-02-01"
    
    url = "https://api.fu.do/v1alpha1/sales"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    # 1. Traer todo febrero
    print("📈 Sincronizando Febrero completo vía API Oficial...")
    params = {
        "page[size]": 500,
        "filter[createdAt]": f"and(gte.{start_feb}T00:00:00Z,lte.{today}T23:59:59Z)"
    }
    
    r = requests.get(url, headers=headers, params=params, timeout=20)
    if r.status_code == 200:
        raw_data = r.json()
        sales = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
        
        daily_stats = {}
        grand_total = 0
        today_total = 0
        
        for s in sales:
            attr = s.get('attributes', {})
            total = float(attr.get('total', 0))
            created_at = attr.get('createdAt', '')[:10]
            
            grand_total += total
            daily_stats[created_at] = daily_stats.get(created_at, 0) + total
            if created_at == today:
                today_total += total
        
        # Guardar para el dashboard
        sorted_days = sorted(daily_stats.keys())
        result = {
            "grand_total": grand_total,
            "today_total": today_total,
            "labels": sorted_days,
            "values": [daily_stats[d] for d in sorted_days],
            "count": len(sales)
        }
        
        with open("c:/Users/Lenovo/clod database/fudo_data_dump/official_stats.json", "w") as f:
            json.dump(result, f)
            
        print(f"✅ SINCRO COMPLETA: ${grand_total} acumulados en Febrero.")
        print(f"✅ VENTAS DE HOY: ${today_total}")

if __name__ == "__main__":
    sync_all_official_data()
