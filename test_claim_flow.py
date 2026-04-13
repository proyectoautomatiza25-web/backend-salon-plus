import requests
import json
import time

def test_claim_by_folio():
    """
    Prueba el proceso de reclamo de puntos por Folio y Monto.
    Simula lo que haría la App móvil.
    """
    url = "http://localhost:8000/api/fudo/reclamar-boleta"
    
    # Datos de prueba (Basados en lo que vimos en Fudo recientemente)
    # Folio 59, Monto ~ $2500 ? (Ajustar según datos reales en Fudo)
    payload = {
        "folio": "59",
        "monto": 2500,
        "whatsapp": "56912345678"
    }
    
    print(f"🧪 Probando RECLAMO DE PUNTOS para Folio {payload['folio']}...")
    print(f"📡 Enviando a {url}...")
    
    try:
        r = requests.post(url, json=payload, timeout=30)
        print(f"📡 STATUS: {r.status_code}")
        
        result = r.json()
        if r.status_code == 200:
            print("✅ EXITO: ", result.get("message"))
            print(f"💰 PUNTOS GANADOS: {result.get('puntos')}")
        else:
            print("❌ FALLO: ", result.get("detail", result))
            
    except Exception as e:
        print(f"💥 Error de conexión: {e}")

if __name__ == "__main__":
    # Asegúrate de que el servidor esté corriendo
    print("Nota: El servidor FastAPI debe estar ejecutándose en localhost:8000")
    test_claim_by_folio()
