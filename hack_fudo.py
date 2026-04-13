import requests
import json
import os
from dotenv import load_dotenv

def hack_fudo_sales():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    # CLONAMOS EXACTAMENTE TU NAVEGADOR SEGUN TU CAPTURA
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "fudo-country-code": "CL",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    # Estos son los endpoints "Hardcore" que sacamos del rastro del navegador
    targets = [
        "https://api.fu.do/summaries", # El que dio 204/200 en la captura
        "https://api.fu.do/cash_registers/1/actions",
        "https://api.fu.do/v2/sales/search",
        "https://api.fu.do/sale_identifiers?per_page=1",
        "https://api.fu.do/sale_summaries?from=2026-02-01&to=2026-02-06"
    ]
    
    print("🕵️‍♂️ Iniciando Infiltración en Fudo (Modo Hack)...")
    
    for url in targets:
        try:
            # Si es /search probamos con POST porque asi lo hace el navegador
            method = requests.post if "search" in url else requests.get
            payload = {"from": "2026-02-05", "to": "2026-02-06"} if "search" in url else None
            
            r = method(url, headers=headers, json=payload, timeout=10)
            print(f"📡 Probando {url} -> {r.status_code}")
            
            if r.status_code in [200, 204, 201]:
                data = r.json() if r.text else {"status": "success_empty"}
                print(f"✅ ¡ACCESO CONCEDIDO! Muestra: {json.dumps(data)[:200]}")
                with open("hacked_sales_data.json", "w") as f:
                    json.dump(data, f)
        except Exception as e:
            print(f"❌ Fallo en {url}: {e}")

if __name__ == "__main__":
    hack_fudo_sales()
