import requests
import json
import os
from dotenv import load_dotenv

def discover_all():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    ruka_id = os.getenv("RUKA_API_ID")
    ruka_key = os.getenv("RUKA_API_KEY")
    fudo_token = os.getenv("FUDO_BEARER_TOKEN")
    
    print("🕵️ Buscando Endpoints...")

    # 1. Probar SUPLAIT.CL (Ruka)
    print("\n📦 Probando SUPLAIT.CL (Ruka alternative)...")
    suplait_headers = {"x-api-id": ruka_id, "x-api-key": ruka_key, "Accept": "application/json"}
    suplait_urls = [
        "https://suplait.cl/api/v1/purchases",
        "https://suplait.cl/api/v1/expenses",
        "https://www.suplait.cl/api/v1/purchases"
    ]
    for url in suplait_urls:
        try:
            r = requests.get(url, headers=suplait_headers, timeout=5)
            print(f"   {url} -> {r.status_code}")
            if r.status_code == 200 and "application/json" in r.headers.get("Content-Type", ""):
                 print(f"      ✅ BINGO RUKA! {str(r.json())[:100]}")
        except: pass

    # 2. Probar FUDO V1
    print("\n🍕 Probando FUDO V1 Endpoints...")
    fudo_headers = {"Authorization": f"Bearer {fudo_token}", "Accept": "application/json"}
    fudo_urls = [
        "https://api.fu.do/sales",
        "https://api.fu.do/v1/sales",
        "https://api.fu.do/orders",
        "https://api.fu.do/v1/orders",
        "https://api.fu.do/sale_summaries"
    ]
    for url in fudo_urls:
        try:
            r = requests.get(url, headers=fudo_headers, timeout=5)
            print(f"   {url} -> {r.status_code}")
            if r.status_code == 200:
                 print(f"      ✅ BINGO FUDO! {str(r.json())[:100]}")
        except: pass

if __name__ == "__main__":
    discover_all()
