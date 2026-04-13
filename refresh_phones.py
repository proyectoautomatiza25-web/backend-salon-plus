import asyncio
from app.services.fudo_sync import FudoSyncService, SUPABASE_URL, SUPABASE_KEY
from app.integrations.fudo_client import FudoClient
import httpx
import json

async def refresh_phones():
    client = FudoClient()
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    # 1. Buscar ventas sin telefono
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{SUPABASE_URL}/rest/v1/ventas_fudo?cliente_telefono=is.null&select=fudo_order_id,id", headers=headers)
        ventas = r.json()
        print(f"Encontradas {len(ventas)} ventas sin teléfono.")
        
        # Procesar en lotes de 20
        for i in range(0, len(ventas), 20):
            batch = ventas[i:i+20]
            for v in batch:
                fid = v['fudo_order_id']
                print(f"Revisando Fudo ID: {fid}...")
                
                # Obtener detalle de Fudo
                # Usamos el motor de FudoSyncService para esto
                auth_headers = client.get_auth_headers()
                sr = await http.get(f"{client.base_url}/sales/{fid}", headers=auth_headers)
                if sr.status_code == 200:
                    sale_data = sr.json()
                    gid = sale_data.get('guestId')
                    if gid:
                        gr = await http.get(f"{client.base_url}/guests/{gid}", headers=auth_headers)
                        if gr.status_code == 200:
                            guest = gr.json()
                            raw_phone = guest.get('phone') or guest.get('mobile') or ""
                            digits = "".join(filter(str.isdigit, str(raw_phone)))
                            
                            telefono_wa = None
                            if digits.startswith("56") and len(digits) == 11: telefono_wa = digits
                            elif digits.startswith("9") and len(digits) == 9: telefono_wa = "56" + digits
                            
                            if telefono_wa:
                                print(f"  -> ¡Encontrado! {telefono_wa}. Actualizando Supabase...")
                                await http.patch(f"{SUPABASE_URL}/rest/v1/ventas_fudo?id=eq.{v['id']}", 
                                                json={"cliente_telefono": telefono_wa}, 
                                                headers=headers)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(refresh_phones())
