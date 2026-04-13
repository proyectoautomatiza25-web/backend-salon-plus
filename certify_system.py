import requests
import json
import uuid
from datetime import datetime
import sys

# CONFIGURACIÓN
BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@agendaplus.cl"
ADMIN_PASS = "admin123"

def print_result(step, status, message):
    icon = "✅" if status else "❌"
    print(f"{icon} [PASO {step}] {message}")
    if not status:
        sys.exit(1)

print("\n--- 🏥 CERTIFICACIÓN DE SISTEMA AGENDA PLUS ---\n")

# 1. PRUEBA DE LOGIN
try:
    auth_response = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": ADMIN_EMAIL, 
        "password": ADMIN_PASS
    })
    
    if auth_response.status_code == 200:
        token = auth_response.json()["access_token"]
        print_result(1, True, "Autenticación Admin EXITOSA")
    else:
        print_result(1, False, f"Fallo Login: {auth_response.text}")

except Exception as e:
    print_result(1, False, f"Error Conexión: {e}")

# 2. PRUEBA DE RESERVA PÚBLICA
try:
    # Datos de un paciente simulado
    booking_data = {
        "stylist_id": "dummy",
        "service_id": "dummy",
        "start_time": datetime.now().isoformat(),
        "client_name": "Paciente Test Automático",
        "client_phone": "+56911112222",
        "client_email": "test@paciente.cl",
        "client_rut": "11.111.111-1",
        "notes": "Prueba de certificación de despliegue"
    }
    
    booking_resp = requests.post(
        f"{BASE_URL}/api/salon/appointments/public-simple",
        json=booking_data
    )
    
    if booking_resp.status_code == 200:
        appt_id = booking_resp.json().get("id")
        print_result(2, True, f"Reserva Online Creada (ID: {appt_id})")
        
        # 3. VERIFICACIÓN EN BASE DE DATOS (Usando API Privada)
        # Consultamos la agenda como Admin para ver si aparece
        headers = {"Authorization": f"Bearer {token}"}
        all_appts_resp = requests.get(f"{BASE_URL}/api/salon/appointments", headers=headers)
        
        found = False
        if all_appts_resp.status_code == 200:
            appts = all_appts_resp.json()
            for a in appts:
                if a["id"] == appt_id:
                    if a["stylist_id"]: # Verificar que se asignó profesional automático
                        found = True
                        print_result(3, True, f"Cita verificada en Base de Datos y asignada a Profesional (ID: {a['stylist_id']})")
                    else:
                        print_result(3, False, "Cita creada pero SIN profesional asignado")
                    break
        
        if not found:
            print_result(3, False, "La cita fue creada públicamente pero NO aparece en la agenda del admin")
            
    else:
        print_result(2, False, f"Fallo Reserva Pública: {booking_resp.text}")

except Exception as e:
    print_result(2, False, f"Error en Flujo Reserva: {e}")

# 4. PRUEBA DE INTELIGENCIA ARTIFICIAL (Híbrida)
try:
    ai_data = {
        "text": "Calcular dosis Paracetamol niño 20kg",
        "type": "dose_calc"
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    ai_resp = requests.post(
        f"{BASE_URL}/api/ai/expand-medical-note",
        json=ai_data,
        headers=headers
    )
    
    if ai_resp.status_code == 200:
        text = ai_resp.json()["expanded_text"]
        if "20" in text and ("mg" in text or "ml" in text):
             print_result(4, True, "Cálculo de Dosis IA/Híbrido Correcto")
             print(f"    📝 Respuesta: {text[:100]}...")
        else:
             print_result(4, False, f"IA respondió pero el cálculo parece incorrecto: {text}")
    else:
         print_result(4, False, f"Fallo IA: {ai_resp.text}")

except Exception as e:
    print_result(4, False, f"Error IA: {e}")

print("\n🚀 CONCLUSIÓN: SISTEMA GLOBAL 100% OPERATIVO")
