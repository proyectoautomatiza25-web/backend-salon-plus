import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def assault_fudo_v2():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    today = date.today().isoformat()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/",
        "fudo-country-code": "CL",
        "fudo-app-version": "2.9.261" # Versión capturada de tus logs
    }

    base_url = "https://api.fu.do"
    
    # OBJETIVOS DE ALTO VALOR (Donde guardan el dinero en v2)
    targets = [
        "v2/orders?per_page=100", # Los pedidos activos/cerrados
        f"v2/sales?from={today}&to={today}", # Las ventas directas
        "v2/dashboard/stats", # El resumen oficial
        "v2/report/sales/daily", # Reporte diario
        f"v2/summaries?date={today}", # Resumen de hoy
        "v2/accounts/191473/sales", # Ruta directa a tu cuenta
        "v2/cash_registers/1/transactions" # Movimientos de plata
    ]
    
    print("🏴‍☠️ INICIANDO ASALTO TOTAL DE DATOS (FUDO v2)...")
    
    spoils = {}
    for t in targets:
        url = f"{base_url}/{t}"
        print(f"🧨 Volando puerta: {url}...", end=" ", flush=True)
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200:
                data = r.json()
                print(f"✅ ¡BOTÍN ENCONTRADO! ({len(json.dumps(data))} bytes)")
                spoils[t] = data
            else:
                print(f"❌ (Fallo {r.status_code})")
        except:
            print("💥 Alarmas disparadas (Timeout)")

    # Guardamos los resultados del asalto
    with open("c:/Users/Lenovo/clod database/fudo_data_dump/asalto_results.json", "w", encoding="utf-8") as f:
        json.dump(spoils, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ Asalto concluido. Puertas abiertas: {len(spoils)}")

if __name__ == "__main__":
    assault_fudo_v2()
