import requests
import json

ACCESS_TOKEN = "APP_USR-6703285773653661-012801-f17be76f714591ed53de2d4beeb4e6fa-3164912896"
PLAN_ID = "2f70c5201dcd4c73ba2217b4aa201950"

url = f"https://api.mercadopago.com/preapproval_plan/{PLAN_ID}"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=4))
else:
    print(f"Error {response.status_code}: {response.text}")
