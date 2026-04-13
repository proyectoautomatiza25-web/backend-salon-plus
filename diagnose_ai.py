import requests
import json
import os
from dotenv import load_dotenv

# Cargar token para autenticarse (simulamos ser admin)
load_dotenv()
USERNAME = "admin@agendaplus.cl"
PASSWORD = "admin123"
BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("--- 🩺 DIAGNÓSTICO DE IA ---")
    
    # 1. Login para obtener token
    print("1. Iniciando sesión...")
    try:
        auth_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": USERNAME, "password": PASSWORD}
        )
        if auth_resp.status_code != 200:
            print(f"❌ Error en Login: {auth_resp.text}")
            return
        
        token = auth_resp.json()["access_token"]
        print("✅ Login exitoso. Token obtenido.")
    except Exception as e:
        print(f"❌ Error de conexión al servidor: {e}")
        return

    # 2. Probar Endpoint de IA
    print("\n2. Enviando solicitud de Dosis Pediátrica...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "text": "Paracetamol, niño de 15kg",
        "type": "dose_calc"
    }
    
    try:
        ai_resp = requests.post(
            f"{BASE_URL}/api/ai/expand-medical-note",
            json=payload,
            headers=headers
        )
        
        if ai_resp.status_code == 200:
            print("\n✅ ÉXITO! Respuesta de Gemini:")
            print("------------------------------------------------")
            print(ai_resp.json()["expanded_text"])
            print("------------------------------------------------")
        else:
            print(f"\n❌ Error en Endpoint IA ({ai_resp.status_code}):")
            print(ai_resp.text)
            
    except Exception as e:
        print(f"❌ Error enviando solicitud: {e}")

if __name__ == "__main__":
    run_test()
