import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"1. Verificando API Key: {'✅ ENCONTRADA' if api_key else '❌ NO ENCONTRADA'}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("2. Intentando conectar con Gemini...")
        response = model.generate_content("Responde solo con la palabra: FUNCIONA")
        
        print(f"3. Respuesta de Gemini: {response.text}")
        print("✅ CONEXIÓN EXITOSA")
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {str(e)}")
else:
    print("❌ No se puede probar sin API Key")
