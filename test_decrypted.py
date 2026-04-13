import requests
import json
import base64

def try_decrypted_auth():
    # 1. El ID decodificado
    user_plain = "36@191473"
    secret = "Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC"
    
    # 2. Creamos el Basic Auth con el ID REAL (no el base64 de antes)
    auth_str = f"{user_plain}:{secret}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Accept": "application/json"
    }

    url = "https://api.fu.do/products?per_page=1"
    
    print(f"🕵️‍♂️ Intentando con ID decodificado: {user_plain}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"📡 STATUS: {r.status_code}")
        if r.status_code == 200:
            print("✅ ¡LOGRADO! El secreto era el ID decodificado.")
            return True
        else:
            print(f"❌ Falló con {r.status_code}")
    except Exception as e:
        print(f"💥 Error: {e}")
        
    return False

if __name__ == "__main__":
    try_decrypted_auth()
