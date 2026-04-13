import requests
import json
import os
from dotenv import load_dotenv

def fish_sales_by_id():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    token = os.getenv("FUDO_BEARER_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Origin": "https://app-v2.fu.do",
        "Referer": "https://app-v2.fu.do/"
    }

    # Cargamos los IDs que ya habiamos bajado
    try:
        with open("c:/Users/Lenovo/clod database/fudo_data_dump/sale_identifiers.json", "r") as f:
            ids_data = json.load(f)
            if isinstance(ids_data, dict):
                ids_list = list(ids_data.values())
            else:
                ids_list = ids_data
    except:
        print("❌ No encontre el archivo de identificadores.")
        return

    print(f"🎣 Intentando pescar {len(ids_list)} ventas por ID...")
    
    real_money = 0
    found_sales = []
    
    for item in ids_list:
        sale_id = item.get('id') if isinstance(item, dict) else item
        url = f"https://api.fu.do/sales/{sale_id}"
        print(f"   📡 Tirando el anzuelo a venta {sale_id}...", end=" ")
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                sale = r.json()
                total = sale.get('amount', sale.get('total', 0))
                real_money += total
                found_sales.append(sale)
                print(f"✅ ¡Pescada! (${total})")
            else:
                print(f"❌ Falló ({r.status_code})")
        except:
            print("💥 Error")

    print(f"\n💰 DINERO TOTAL CALCULADO: {real_money}")
    
    # Guardamos el resultado del hack
    with open("c:/Users/Lenovo/clod database/fudo_data_dump/real_sales_fished.json", "w") as f:
        json.dump({"total_ventas": real_money, "sales": found_sales}, f)

if __name__ == "__main__":
    fish_sales_by_id()
