#!/usr/bin/env python3
"""
Script para probar el login en el backend LOCAL
"""
import requests

def test_local_login():
    print("=" * 60)
    print("  PRUEBA DE LOGIN EN BACKEND LOCAL")
    print("=" * 60)
    print()
    
    api_url = "http://127.0.0.1:8000/api/auth/login"
    email = "admin@agendaplus.cl"
    password = "admin123"
    
    print(f"📡 Probando login en: {api_url}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print()
    
    try:
        response = requests.post(
            api_url,
            data={
                "username": email,
                "password": password
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN EXITOSO!")
            print(f"   Token: {data.get('access_token', '')[:80]}...")
            print(f"   Token Type: {data.get('token_type', '')}")
            print()
            
            # Probar el endpoint /me
            print("📡 Probando endpoint /me...")
            me_response = requests.get(
                "http://127.0.0.1:8000/api/auth/me",
                headers={
                    "Authorization": f"Bearer {data['access_token']}"
                }
            )
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ Usuario obtenido:")
                print(f"   ID: {user_data.get('id')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Business: {user_data.get('business_name')}")
                print()
                print("🎉 TODO FUNCIONA CORRECTAMENTE!")
            else:
                print(f"❌ Error en /me: {me_response.status_code}")
                print(f"   {me_response.text}")
            
            return True
        else:
            print(f"❌ ERROR EN LOGIN:")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    test_local_login()
