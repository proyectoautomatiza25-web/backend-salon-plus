import requests
from requests.auth import HTTPBasicAuth
import itertools

# Datos base
CLIENT_ID = "MDAwMDI6MTkxNDcz"
# El secreto base con caracteres dudosos (I/l)
# DbJcsn8gNJY[I/l]3[I/l]OMwVmkMUCx
SECRET_PREFIX = "DbJcsn8gNJY"
SECRET_SUFFIX = "OMwVmkMUCx"
MIDDLE_CHAR_1_OPTIONS = ["I", "l"] # Posibles valores para el primer caracter dudoso
MIDDLE_CHAR_2_OPTIONS = ["I", "l"] # Posibles valores para el segundo caracter dudoso

# URL base correcta segun captura app-v2
URLS_TO_TEST = [
    "https://app-v2.fu.do/api",
    "https://api.fu.do",
    "https://app-v2.fu.do"
]

def bruteforce_fudo():
    print("🔓 Iniciando descifrado de credenciales Fudo...")
    
    # Generar combinaciones
    combinations = list(itertools.product(MIDDLE_CHAR_1_OPTIONS, MIDDLE_CHAR_2_OPTIONS))
    
    for char1, char2 in combinations:
        # Construir secreto candidato
        # Asumimos que el "3" es un numero fijo entre medias
        candidate_secret = f"{SECRET_PREFIX}{char1}3{char2}{SECRET_SUFFIX}"
        
        print(f"👉 Probando secreto: ...{char1}3{char2}...")
        
        for base_url in URLS_TO_TEST:
            try:
                # Probar endpoint inocuo (Products o Sales)
                target_url = f"{base_url}/sales"
                
                # Probar Basic Auth (Metodo mas estandar)
                r = requests.get(
                    target_url, 
                    auth=HTTPBasicAuth(CLIENT_ID, candidate_secret),
                    headers={"User-Agent": "Test/1.0", "Accept": "application/json"},
                    timeout=5
                )
                
                if r.status_code == 200:
                    print(f"\n✅ ¡EUREKA! CREDENCIALES ENCONTRADAS")
                    print(f"   URL: {base_url}")
                    print(f"   Secreto Correcto: {candidate_secret}")
                    print(f"   Datos obtenidos: {len(r.json())} registros")
                    return
                elif r.status_code != 404 and r.status_code != 401:
                    # Si da algo distinto a rechazo o no encontrado (ej: 403 Forbidden pero autenticado)
                    print(f"   ⚠️ Respuesta interesante ({r.status_code}) en {base_url}")

            except Exception as e:
                pass # Ignorar errores de conexion, seguir probando

    print("\n❌ Fin de pruebas. Ninguna combinación funcionó (o el endpoint no es /sales o /products).")

if __name__ == "__main__":
    bruteforce_fudo()
