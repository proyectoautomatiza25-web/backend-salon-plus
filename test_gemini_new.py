from google import genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"1. Verificando API Key: {'✅ ENCONTRADA' if api_key else '❌ NO ENCONTRADA'}")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        
        print("2. Intentando conectar con Gemini 1.5 Flash...")
        response = client.models.generate_content(
            model='gemini-1.5-flash', contents="Responde solo con la palabra: FUNCIONA"
        )
        
        print(f"3. Respuesta de Gemini: {response.text}")
        print("✅ CONEXIÓN EXITOSA")
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {str(e)}")
else:
    print("❌ No se puede probar sin API Key")
