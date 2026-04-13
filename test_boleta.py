"""Test rápido del endpoint buscar-boleta"""
import urllib.request
import json

url = 'http://localhost:8000/api/fudo/buscar-boleta?folio=59&fecha=2026-02-06'
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.loads(r.read())
        print('SUCCESS:', data.get('success'))
        print('Total encontradas:', data.get('total_encontradas'))
        print('Mensaje:', data.get('mensaje', ''))
        ventas = data.get('ventas', data.get('ventas_del_dia', []))
        print(f'Ventas retornadas: {len(ventas)}')
        for v in ventas[:5]:
            sid = v.get('id')
            attrs = v.get('attributes', {})
            status = attrs.get('invoicingStatus', '?')
            total = attrs.get('total', 0)
            fiscal = v.get('_detalle_fiscal', {})
            print(f'  Venta #{sid}: {status} - Total: ${total} | Folio: {fiscal.get("folio","N/A")}')
except Exception as e:
    print('ERROR:', e)
