import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings()

DOMAINS = [
    "https://app-v2.fu.do",
    "https://api.fu.do"
]

PATHS = [
    "/sales",
    "/api/sales", 
    "/api/v1/sales",
    "/api/integrations/orders"
]

CREDS = ("MDAwMDI6MTkxNDcz", "DbJcsn8gNJYI3IOMwVmkMUCx")

def run():
    print("🕵️ Iniciando Sondeo de Endpoints Fudo...")
    print("-" * 50)
    
    headers = {"Accept": "application/json", "User-Agent": "TestClient/1.0"}
    
    for domain in DOMAINS:
        print(f"\n🌍 Dominio: {domain}")
        for path in PATHS:
            url = f"{domain}{path}"
            try:
                # 1. Sin Auth
                r = requests.get(url, headers=headers, verify=False, timeout=3)
                status = r.status_code
                
                # 2. Con Auth (solo si 401/403)
                auth_status = "N/A"
                if status in [401, 403]:
                    r2 = requests.get(url, headers=headers, auth=CREDS, verify=False, timeout=3)
                    auth_status = str(r2.status_code)
                
                mark = "✅" if status in [200, 401, 403] else "❌" # 401/403 es bueno (existe endpoint)
                if status == 404: mark = "💀" # Muerto
                
                print(f"   {mark} {path:<25} -> Status: {status} (Auth: {auth_status})")
                
            except Exception as e:
                print(f"   ⚠️ {path:<25} -> Error: {str(e)[:30]}")

if __name__ == "__main__":
    run()
