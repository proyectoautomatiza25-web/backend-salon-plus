import os
import requests
from dotenv import load_dotenv

load_dotenv()

RUKA_API_ID = os.getenv("RUKA_API_ID", "a4f92c1e7b6d4a0a6c83f1d2b5e67890")
RUKA_API_KEY = os.getenv("RUKA_API_KEY", "f18c3d4a0b9e8625d1e7c890e2b654ff")
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "cPlq6mXKRR33wFhcOj4JrT3x7KB5aZxG")

def test_whapi():
    print("Testing Whapi...")
    url = "https://gate.whapi.cloud/settings"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {WHAPI_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        print(f"Whapi Status: {response.status_code}")
        if response.status_code == 200:
            print("Whapi Config:", response.json())
        else:
            print("Whapi Error:", response.text)
    except Exception as e:
        print("Whapi Connection Error:", e)

if __name__ == "__main__":
    test_whapi()
