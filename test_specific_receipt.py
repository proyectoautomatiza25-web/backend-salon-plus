import asyncio
import os
from datetime import datetime
from app.integrations.fudo_client import FudoClient
from dotenv import load_dotenv

async def check_receipt_5982():
    load_dotenv()
    client = FudoClient()
    
    # Buscamos las ventas del 8 de Abril de 2026
    desde = datetime(2026, 4, 8, 0, 0, 0)
    hasta = datetime(2026, 4, 8, 23, 59, 59)
    
    print(f"--- Buscando venta #5982 en Fudo (Dia {desde.date()}) ---")
    
    # 1. Obtener ventas del dia
    sales = await client.fetch_orders(desde, hasta)
    print(f"Total ventas encontradas en el periodo: {len(sales)}")
    
    # 2. Buscar por el identificador corto '5982'
    match = None
    for s in sales:
        # Fudo suele tener un campo 'number' o 'id' corto en el Panel.
        # En la API oficial, el 'number' es el correlativo diario.
        attrs = s.get('attributes', {})
        number = s.get('number') or attrs.get('number')
        
        if str(number) == '5982':
            match = s
            break
            
    if match:
        print("MATCH ENCONTRADO!")
        print(f"ID: {match.get('id')}")
        print(f"Monto: {match.get('total') or match.get('attributes', {}).get('total')}")
        print(f"Items: {len(match.get('additions', []))}")
        return True
    else:
        print("No se encontro un match exacto con el numero '5982'.")
        # Mostrar los primeros numeros encontrados para debug
        nums = [str(s.get('number') or s.get('attributes', {}).get('number')) for s in sales[:10]]
        print(f"Numeros encontrados (primeros 10): {', '.join(nums)}")
        return False

if __name__ == "__main__":
    asyncio.run(check_receipt_5982())
