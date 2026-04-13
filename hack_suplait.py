import requests
import json
import os
from dotenv import load_dotenv

def hack_suplait_expenses():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    # Suplait suele usar una API Key o el mismo token si estan vinculados
    api_key = os.getenv("RUKA_API_KEY") 
    
    # Probamos las rutas secretas de Suplait (Post-Ruka)
    targets = [
        "https://api.suplait.cl/v1/purchases",
        "https://api.suplait.com/v1/expenses",
        "https://app.suplait.cl/api/v1/invoices",
        "https://api.ruka.ai/v1/purchases"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }

    print("🕵️‍♂️ Escaneando servidores de Suplait/Ruka...")
    
    found_expenses = []
    for url in targets:
        try:
            print(f"📡 Probando {url}...", end=" ")
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                print("✅ ¡INFILTRACIÓN EXITOSA!")
                data = r.json()
                found_expenses = data.get('data', data)
                with open("c:/Users/Lenovo/clod database/fudo_data_dump/gastos_reales.json", "w") as f:
                    json.dump(data, f)
                return found_expenses
            else:
                print(f"❌ (Error {r.status_code})")
        except:
            print("💥 Off-line")
            
    return None

if __name__ == "__main__":
    hack_suplait_expenses()
