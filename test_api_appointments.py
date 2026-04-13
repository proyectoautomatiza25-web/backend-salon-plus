#!/usr/bin/env python3
"""
Verificar que el API devuelve las citas correctamente
"""
import requests

# Login
login_response = requests.post(
    'http://127.0.0.1:8000/api/auth/login',
    data={
        'username': 'admin@agendaplus.cl',
        'password': 'admin123'
    }
)

print("=" * 70)
print("  VERIFICACIÓN DEL API - CITAS")
print("=" * 70)
print()

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print(f"✅ Login exitoso")
    print()
    
    # Obtener citas
    appointments_response = requests.get(
        'http://127.0.0.1:8000/api/salon/appointments',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if appointments_response.status_code == 200:
        citas = appointments_response.json()
        print(f"✅ API devuelve {len(citas)} citas")
        print()
        
        for c in citas:
            print(f"📅 {c['start_time']}")
            print(f"   Cliente ID: {c['client_id']}")
            print(f"   Profesional ID: {c['stylist_id']}")
            print()
    else:
        print(f"❌ Error al obtener citas: {appointments_response.status_code}")
        print(appointments_response.text)
else:
    print(f"❌ Error en login: {login_response.status_code}")
    print(login_response.text)
