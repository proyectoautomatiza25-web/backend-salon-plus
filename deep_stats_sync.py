import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

def get_official_fudo_token():
    load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")
    api_key = os.getenv("FUDO_CLIENT_ID")
    api_secret = os.getenv("FUDO_CLIENT_SECRET")
    auth_url = "https://auth.fu.do/api"
    payload = {"apiKey": api_key, "apiSecret": api_secret}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    try:
        r = requests.post(auth_url, json=payload, headers=headers, timeout=10)
        return r.json().get("token") if r.status_code == 200 else None
    except: return None

def deep_stats_sync():
    token = get_official_fudo_token()
    if not token: return
    
    today = date.today().isoformat()
    start_feb = "2026-02-01"
    
    # Cargar mapa de productos para nombres
    try:
        with open("c:/Users/Lenovo/clod database/fudo_data_dump/products.json", "r", encoding="utf-8") as f:
            prods_data = json.load(f)
            prods = prods_data.values() if isinstance(prods_data, dict) else (prods_data.get('data', prods_data) if isinstance(prods_data, dict) else prods_data)
            prod_map = {str(p['id']): p['name'] for p in prods if isinstance(p, dict) and 'id' in p}
    except:
        prod_map = {}

    url = "https://api.fu.do/v1alpha1/sales"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    print("📈 Iniciando Sincronización PROFUNDA de Febrero (Metodología v1alpha1 + Quantities)...")
    
    product_stats = {} # ID -> {'count': total_qty, 'name': name}
    daily_stats = {}
    grand_total = 0
    today_total = 0
    total_sales_count = 0
    
    page = 1
    has_more = True
    
    while has_more:
        # Crucial: include=items para obtener las lineas de venta y cantidades
        params = {
            "page[size]": 100, # Bajamos a 100 para no saturar el include
            "page[number]": page,
            "filter[createdAt]": f"and(gte.{start_feb}T00:00:00Z,lte.{today}T23:59:59Z)",
            "include": "items"
        }
        
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code != 200: break
            
            data = r.json()
            sales = data.get('data', [])
            included = data.get('included', [])
            
            if not sales: break
            
            # Mapear los items incluidos por su ID para acceso rapido
            items_map = {item['id']: item for item in included if item['type'] == 'Item'}
            
            for s in sales:
                attr = s.get('attributes', {})
                total = float(attr.get('total', 0))
                created_at = attr.get('createdAt', '')[:10]
                
                grand_total += total
                total_sales_count += 1
                daily_stats[created_at] = daily_stats.get(created_at, 0) + total
                if created_at == today:
                    today_total += total
                
                # Procesar lineas de venta
                items_rel = s.get('relationships', {}).get('items', {}).get('data', [])
                for item_ref in items_rel:
                    item_id = item_ref.get('id')
                    item_data = items_map.get(item_id)
                    
                    if item_data:
                        # Sacar ID del producto y cantidad
                        qty = float(item_data.get('attributes', {}).get('quantity', 1.0))
                        prod_id = str(item_data.get('relationships', {}).get('product', {}).get('data', {}).get('id'))
                        
                        if prod_id != 'None':
                            if prod_id not in product_stats:
                                product_stats[prod_id] = {'qty': 0, 'name': prod_map.get(prod_id, f"Producto {prod_id}")}
                            product_stats[prod_id]['qty'] += qty
            
            print(f"📡 Procesada página {page} ({len(sales)} ventas)...")
            if len(sales) < 100: has_more = False
            else: page += 1
        except Exception as e:
            print(f"💥 Error en página {page}: {e}")
            break

    # Calcular rankings reales
    sorted_prods = sorted(product_stats.items(), key=lambda x: x[1]['qty'], reverse=True)
    
    top_items = []
    for p_id, info in sorted_prods[:5]:
        top_items.append({"name": info['name'], "sold": int(info['qty'])})
        
    bottom_items = []
    for p_id, info in sorted_prods[-5:]:
        bottom_items.append({"name": info['name'], "sold": int(info['qty'])})

    result = {
        "grand_total": grand_total,
        "today_total": today_total,
        "labels": sorted(daily_stats.keys()),
        "values": [daily_stats[d] for d in sorted(daily_stats.keys())],
        "count": total_sales_count,
        "top_sold": top_items,
        "bottom_sold": bottom_items,
        "star_product": top_items[0] if top_items else {"name": "N/A", "sold": 0}
    }
    
    with open("c:/Users/Lenovo/clod database/fudo_data_dump/deep_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
        
    print(f"✅ ANALISIS FINALIZADO: {total_sales_count} ventas analizadas.")
    print(f"⭐ PRODUCTO ESTRELLA: {result['star_product']['name']} ({result['star_product']['sold']} unidades)")

if __name__ == "__main__":
    deep_stats_sync()
