import requests
import json
import os
from dotenv import load_dotenv

def download_everything():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/"
    }
    
    base_url = "https://api.fu.do"
    dump_dir = "c:/Users/Lenovo/clod database/fudo_data_dump"
    
    # Lista de endpoints detectados en tus capturas
    endpoints = [
        "account", "settings", "roles", "payment_types", "sale_identifiers",
        "ingredients", "products", "product_categories", "guests", "users",
        "electronic_invoice_settings", "taxes", "external_apps", "kitchens",
        "rooms", "cash_registers", "tables"
    ]
    
    print(f"🚀 Iniciando DESCARGA TOTAL de Kingdom Coffee...")
    
    summary = {}
    
    for ep in endpoints:
        url = f"{base_url}/{ep}"
        print(f"📥 Descargando: {ep}...", end=" ", flush=True)
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                # Extraer la lista si viene envuelta en 'data'
                items = data.get('data', data) if isinstance(data, dict) else data
                count = len(items) if isinstance(items, (list, dict)) else 1
                
                file_path = os.path.join(dump_dir, f"{ep}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ ({count} registros)")
                summary[ep] = count
            else:
                print(f"❌ Error {r.status_code}")
        except Exception as e:
            print(f"💥 Error: {e}")

    # Guardar resumen final
    with open(os.path.join(dump_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n✨ ¡DESCARGA COMPLETADA! Todos los archivos están en la carpeta 'fudo_data_dump'.")

if __name__ == "__main__":
    download_everything()
