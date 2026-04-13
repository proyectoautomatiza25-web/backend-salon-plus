import requests
import os
from dotenv import load_dotenv

load_dotenv()
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "cPlq6mXKRR33wFhcOj4JrT3x7KB5aZxG")

def test_whapi_message():
    url = "https://gate.whapi.cloud/messages/text"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {WHAPI_TOKEN}",
        "content-type": "application/json"
    }
    
    # Intenta hacer un fetch simple a los canales de la cuenta para validar estado
    print("----- Checking WHAPI Status -----")
    check_url = "https://gate.whapi.cloud/health"
    try:
        res = requests.get(check_url, headers={"authorization": f"Bearer {WHAPI_TOKEN}"})
        print(f"Health Response {res.status_code}:", res.text)
    except Exception as e:
        print("Error:", e)

    check_settings = "https://gate.whapi.cloud/settings"
    try:
        res = requests.get(check_settings, headers={"authorization": f"Bearer {WHAPI_TOKEN}"})
        print(f"Settings Response {res.status_code}:", res.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_whapi_message()
