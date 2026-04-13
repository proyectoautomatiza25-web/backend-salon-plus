import requests
import base64

def probe_key(key):
    # Base URL for General Purpose API (as mentioned in documentation guides in the project)
    base_url = "https://api.fu.do/v1" 
    
    print(f"Testing key: {key}")
    
    # Try as Bearer
    print("\n1. Trying as Bearer Token...")
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    try:
        r = requests.get(f"{base_url}/sales", headers=headers, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ Success as Bearer!")
            print(f"   Data: {str(r.json())[:100]}...")
            return
    except Exception as e:
        print(f"   Error: {e}")

    # Try as Basic Auth Username (with empty password)
    print("\n2. Trying as Basic Auth (key:)...")
    auth_str = base64.b64encode(f"{key}:".encode()).decode()
    headers = {"Authorization": f"Basic {auth_str}", "Accept": "application/json"}
    try:
        r = requests.get(f"{base_url}/sales", headers=headers, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ Success as Basic Auth (empty password)!")
            return
    except Exception as e:
        print(f"   Error: {e}")

    # Try as X-API-Key header (common in some APIs)
    print("\n3. Trying as X-API-Key header...")
    headers = {"X-API-Key": key, "Accept": "application/json"}
    try:
        r = requests.get(f"{base_url}/sales", headers=headers, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ Success with X-API-Key header!")
            return
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    probe_key("MzZAMTkxNDcz")
