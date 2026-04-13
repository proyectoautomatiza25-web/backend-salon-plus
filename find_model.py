from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# Lista de modelos probables
models_to_try = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.0-pro"
]

print(f"Probando modelos con tu API Key...")

for model_name in models_to_try:
    try:
        print(f"Intentando: {model_name}...", end=" ")
        response = client.models.generate_content(
            model=model_name, 
            contents="Hola"
        )
        print("✅ FUNCIONA!")
        print(f"--> USAREMOS: {model_name}")
        
        # Guardar el nombre del modelo que funcionó
        with open("working_model.txt", "w") as f:
            f.write(model_name)
        break
    except Exception as e:
        print(f"❌ Falló ({e})")
