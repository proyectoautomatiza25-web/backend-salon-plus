from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    print("Listando modelos disponibles...")
    # Listar modelos es ligeramente diferente, intentemos una llamada generica primero
    # O probemos gemini-pro que es más estandar
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp', contents="Test"
    )
    print("Gemini 2.0 Flash funciona")
except Exception as e:
    print(f"Error 2.0: {e}")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-1.5-flash-001', contents="Test"
    )
    print("Gemini 1.5 Flash 001 funciona")
except Exception as e:
    print(f"Error 1.5: {e}")
