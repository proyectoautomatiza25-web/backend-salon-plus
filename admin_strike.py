import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from datetime import date, timedelta

def admin_power_strike():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    # Tus credenciales de Admin
    user_id = "36@191473"
    secret = "Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC"
    
    # Rango de fechas: Todo febrero hasta hoy
    today = date.today().isoformat()
    start_feb = "2026-02-01"
    
    auth = HTTPBasicAuth(user_id, secret)
    headers = {"Accept": "application/json", "User-Agent": "Kingdom-Command-v4"}

    print(f"🕵️‍♂️ LANZANDO ATAQUE CON RANGO ADMIN (User: {user_id})...")
    
    # 1. Probar acceso a la lista de usuarios (Solo admins pueden)
    print("👥 Verificando Rango Admin en /users...", end=" ")
    try:
        ru = requests.get("https://api.fu.do/users", auth=auth, headers=headers, timeout=10)
        if ru.status_code == 200:
            print("✅ ¡CONFIRMADO! Eres Admin del sistema.")
        else:
            print(f"❌ (Status {ru.status_code})")
    except: print("💥 Fallo")

    # 2. El Gran Atraco: Ventas de Febrero
    url_sales = f"https://api.fu.do/sales?from={start_feb}&to={today}"
    print(f"💰 Extrayendo Ventas de FEBRERO ({start_feb} al {today})...", end=" ")
    
    try:
        rs = requests.get(url_sales, auth=auth, headers=headers, timeout=15)
        if rs.status_code == 200:
            data = rs.json()
            items = data.get('data', data)
            if isinstance(items, dict): items = list(items.values())
            
            total = sum(float(s.get('amount', 0)) for s in items)
            print(f"✅ ¡BINGO! Total Febrero: ${total}")
            
            # Guardamos el botín para el dashboard
            with open("c:/Users/Lenovo/clod database/fudo_data_dump/admin_sales_february.json", "w") as f:
                json.dump({"total_bruto": total, "operaciones": len(items), "detalles": items}, f)
            return True
        else:
            print(f"❌ (Status {rs.status_code})")
            print(f"   Mensaje: {rs.text[:100]}")
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        
    return False

if __name__ == "__main__":
    admin_power_strike()
