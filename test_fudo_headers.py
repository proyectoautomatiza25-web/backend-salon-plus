import requests
import json
import base64

# Credenciales
CLIENT_ID = "MDAwMDI6MTkxNDcz"
CLIENT_SECRET = "DbJcsn8gNJYI3IOMwVmkMUCx"
BASE_URL = "https://api.fu.do"

def test_api_key_method():
    print(f"🔑 Probando autenticación vía Headers directos...")
    
    # Metodo 3: Headers X-API-Key (Estilo moderno)
    headers = {
        "User-Agent": "FocusApp test",
        "Accept": "application/json",
        "X-Client-Id": CLIENT_ID,   # Posibles variaciones
        "X-Client-Secret": CLIENT_SECRET,
        "Authorization": CLIENT_SECRET # A veces el secret actua como Bearer directamente
    }
    
    try:
        # endpoint simple
        print("   INTENTO A: Headers Custom (X-Client-Id)...")
        r = requests.get(f"{BASE_URL}/sales", headers=headers)
        print(f"   Status: {r.status_code}")
        
    except Exception as e: print(e)
    
    try:
        # Metodo 4: Basic Auth pero sin codificar manual (requests lo hace)
        print("\n   INTENTO B: Basic Auth Estandar...")
        r = requests.get(f"{BASE_URL}/sales", auth=(CLIENT_ID, CLIENT_SECRET))
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ FUNCIONÓ Basic Auth!")
            return
            
    except Exception as e: print(e)

if __name__ == "__main__":
    test_api_key_method()
