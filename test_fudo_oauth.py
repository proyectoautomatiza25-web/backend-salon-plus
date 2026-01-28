import requests
from requests.auth import HTTPBasicAuth
import json
import base64

# Credenciales
CLIENT_ID = "MDAwMDI6MTkxNDcz"
CLIENT_SECRET = "DbJcsn8gNJYI3IOMwVmkMUCx"
BASE_URL = "https://api.fu.do"

def get_access_token():
    print(f"🔑 Solicitando Token OAuth a {BASE_URL}...")
    
    # Intento comun de OAuth 2.0 Client Credentials
    auth_url = f"{BASE_URL}/oauth/token" # URL estandar probable
    # A veces es /v1/oauth/token o simplemente /token
    
    # 1. Probar URL estandar
    try:
        # Algunos requieren Basic Auth del ClientID:Secret
        auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        
        payload = {'grant_type': 'client_credentials'}
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post("https://api.fu.do/intro/token", data=payload, headers=headers)
        # Nota: La URL /intro/token es a veces usada por sistemas legacy, probaré varias.
        
        if response.status_code != 200:
             # Probar endpoint comun v2
             response = requests.post("https://api.fu.do/v1/oauth/token", data=payload, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Token recibido!")
            return token_data.get('access_token')
        else:
            print(f"   ⚠️ Fallo metodo 1 ({response.status_code}): {response.text}")
            
            # Intento 2: JSON Body en lugar de Header
            print("   🔄 Intentando metodo alternativo (Body JSON)...")
            json_payload = {
                "clientId": CLIENT_ID,
                "clientSecret": CLIENT_SECRET,
                "grantType": "client_credentials" 
            }
            response = requests.post("https://api.fu.do/auth/token", json=json_payload)
            if response.status_code == 200:
                 token_data = response.json()
                 return token_data.get('access_token')
            else:
                 print(f"   ❌ Fallo total auth: {response.text}")
                 
    except Exception as e:
        print(f"   ❌ Error critico auth: {e}")
    return None

def test_data(token):
    if not token:
        return
        
    print("\n📡 Conectando a datos con Token...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    # 1. Ventas
    try:
        r = requests.get(f"{BASE_URL}/sales", headers=headers)
        print(f"   📊 GET /sales: {r.status_code}")
        if r.status_code == 200:
            print(f"      ✅ {len(r.json())} ventas encontradas")
    except: pass

if __name__ == "__main__":
    # Vamos a probar la autenticacion 
    # Nota: Si Fudo usa una URL muy especifica que no es publica,
    # podria fallar sin la documentacion exacta.
    # Pero Client Credentials es el estandar industrial.
    
    token = get_access_token()
    # Si falla, imprimire instrucciones para que el usuario revise su documentacion Fudo
