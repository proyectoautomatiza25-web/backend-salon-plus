import requests

def test_key_headers(key):
    url = "https://api.fu.do/v1/sales"
    headers_to_try = [
        {"Authorization": f"Bearer {key}"},
        {"Authorization": f"Token {key}"},
        {"X-API-Key": key},
        {"X-Fudo-Access-Token": key},
        {"api-key": key},
        {"apikey": key}
    ]
    
    print(f"Testing key: {key} against {url}")
    for headers in headers_to_try:
        header_name = list(headers.keys())[0]
        print(f"   Trying {header_name}...")
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                print(f"   ✅ SUCCESS with {headers}")
                return
            else:
                print(f"   Failed ({r.status_code})")
        except:
            pass

if __name__ == "__main__":
    test_key_headers("MzZAMTkxNDcz")
