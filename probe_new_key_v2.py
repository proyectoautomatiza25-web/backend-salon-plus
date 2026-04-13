import requests
import base64

def probe_with_secret(client_id, secret):
    url = "https://app-v2.fu.do/api/integrations/orders"
    print(f"Testing Client ID: {client_id} with existing secret")
    
    auth_str = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_str}",
        "Accept": "application/json"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ SUCCESS!")
            print(f"   Data: {str(r.json())[:100]}...")
        else:
            print(f"   Failed: {r.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    existing_secret = "DbJcsn8gNJYI3IOMwVmkMUCx"
    new_key = "MzZAMTkxNDcz"
    probe_with_secret(new_key, existing_secret)
