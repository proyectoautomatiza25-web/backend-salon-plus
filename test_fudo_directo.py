"""Test directo a Fudo API para entender el formato del filtro de fecha"""
import urllib.request
import urllib.parse
import json
import os

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhaSI6MTkxNDczLCJ1aSI6MzYsImV4cCI6MTc3MDg2Njg0MX0.QtDb4t3v5SLP9jXTEGOJegSBhegc7a34dya_VgPDdek"

tests = [
    # Test 1: sin filtro
    "https://api.fu.do/v1alpha1/sales?page[size]=5",
    # Test 2: filtro con UTC
    "https://api.fu.do/v1alpha1/sales?filter[closedAt]=and(gte.2026-02-06T00:00:00Z,lte.2026-02-06T23:59:59Z)&page[size]=5",
    # Test 3: filtro simple gte
    "https://api.fu.do/v1alpha1/sales?filter[closedAt]=gte.2026-02-06T00:00:00Z&page[size]=5",
]

for url in tests:
    print(f"\nTesting: {url[:80]}...")
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            ventas = data.get('data', [])
            print(f"  OK - {len(ventas)} ventas")
            if ventas:
                v = ventas[0]
                attrs = v.get('attributes', {})
                print(f"  Primera venta: id={v.get('id')}, closedAt={attrs.get('closedAt')}, invoicingStatus={attrs.get('invoicingStatus')}")
    except Exception as e:
        print(f"  ERROR: {e}")
