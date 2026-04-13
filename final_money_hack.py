import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def last_hack_attempt():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    today = date.today().isoformat()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "fudo-country-code": "CL"
    }

    # El endpoint definitivo para el Dashboard de Fudo v2 es /v2/summaries o via search
    # Pero vamos a intentar sacar el reporte diario de caja directamente
    url = f"https://api.fu.do/summaries?from={today}&to={today}"
    
    print(f"🔥 LANZANDO ÚLTIMO HACK AL TOTAL DE VENTAS ({today})...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"📡 {url} -> {r.status_code}")
        if r.status_code == 200:
            print("✅ ¡BINGO ABSOLUTO! Dinero real en mano.")
            with open("total_ventas_real.json", "w") as f:
                json.dump(r.json(), f)
            return True
        else:
            # Plan C: Intentar por la ruta de facturacion
            print("🕵️ Buscando en facturacion electronica...")
            r2 = requests.get("https://api.fu.do/electronic_invoice_settings", headers=headers)
            if r2.status_code == 200:
                print("✅ Acceso a facturacion concedido.")
                with open("facturacion_real.json", "w") as f:
                    json.dump(r2.json(), f)
    except: pass
    return False

if __name__ == "__main__":
    last_hack_attempt()
