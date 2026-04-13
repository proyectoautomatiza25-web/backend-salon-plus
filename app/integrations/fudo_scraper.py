import os
import json
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlencode

# Playwright para emular navegador
from playwright.async_api import async_playwright
import httpx

class FudoScraper:
    def __init__(self):
        from dotenv import load_dotenv
        # Ubicar .env en la raiz del modulo backend
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))
        
        self.email = os.getenv("FUDO_LOGIN_EMAIL")
        self.password = os.getenv("FUDO_LOGIN_PASSWORD")
        self.internal_token: Optional[str] = None

    async def get_internal_token(self) -> str:
        """
        Emula un navegador para hacer login en Fudo y capturar el token interno
        con el que funciona el Panel, el cual no tiene las restricciones de las apikeys publicas.
        """
        if self.internal_token:
            return self.internal_token

        if not self.email or not self.password:
            raise ValueError("Faltan credenciales web de Fudo en el .env: FUDO_LOGIN_EMAIL o FUDO_LOGIN_PASSWORD")

        print("[Scraper] Iniciando navegador oculto para login...")
        
        async with async_playwright() as p:
            # Usar chromium headless
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()

            token_captured = asyncio.Future()

            # Interceptar y capturar el Token Bearer de la API interna
            async def handle_request(request):
                # Fudo panel suele consultar api.fu.do
                url = request.url
                if "api.fu.do" in url and "Authorization" in request.headers:
                    auth_header = request.headers["Authorization"]
                    if auth_header.startswith("Bearer "):
                        if not token_captured.done():
                            token_captured.set_result(auth_header)

            page.on("request", handle_request)

            try:
                # Vamos al login de fudo
                print("[Scraper] Accediendo a app-v2.fu.do...")
                await page.goto("https://app-v2.fu.do", wait_until="networkidle")

                # Seleccionar los inputs (correo y pass). 
                print("[Scraper] Rellenando credenciales...")
                
                await page.wait_for_selector('input#user')
                await page.fill('input#user', self.email)
                
                password_input = await page.query_selector('input#password')
                if not password_input:
                    await page.keyboard.press("Enter")
                    await page.wait_for_selector('input#password', state="visible", timeout=10000)
                
                await page.fill('input#password', self.password)
                await page.keyboard.press("Enter")

                print("[Scraper] Esperando validacion y carga de Dashboard...")
                
                auth_header = await asyncio.wait_for(token_captured, timeout=15.0)
                
                self.internal_token = auth_header.replace("Bearer ", "")
                print(f"[Scraper] ¡Token interno capturado con exito! ({self.internal_token[:15]}...)")
                
                return self.internal_token

            except asyncio.TimeoutError:
                print("[Scraper] No se detecto el token por trafico, intentando por LocalStorage...")
                try:
                    state = await context.storage_state()
                    origins = state.get("origins", [])
                    pass
                except Exception:
                    pass
                raise Exception("Tiempo de espera agotado al intentar iniciar sesion en Fudo. Revisa tus credenciales.")
            except Exception as e:
                raise Exception(f"Fallo en el Scraping de Login: {str(e)}")
            finally:
                await browser.close()
    
    async def get_raw_sales(self, from_date: str, to_date: str) -> Dict[str, Any]:
        """
        Con el token de extraccion, consultar el endpoint privado que usa el Panel Web 
        (que es mas permisivo y robusto).
        """
        token = await self.get_internal_token()
        
        url = "https://api.fu.do/v2/sales"
        params = {
            "from": from_date,
            "to": to_date,
            "per_page": 200
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"Fallo extraccion de datos v2: {resp.status_code} - {resp.text}")
            return resp.json()

    async def get_sale_detail(self, sale_id: str) -> Dict[str, Any]:
        """
        Obtener el detalle real incluyendo el numero de boleta oficial si es que tiene.
        """
        token = await self.get_internal_token()
        url = f"https://api.fu.do/v2/sales/{sale_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"Fallo extraccion de detalle v2: {resp.status_code} - {resp.text}")
            return resp.json()

# Para testear el script localmente
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    
    async def test():
        scraper = FudoScraper()
        
        # Necesitamos la fecha de hoy para testear
        from datetime import date
        today = date.today().isoformat()
        
        try:
            print("Iniciando prueba de scraper...")
            sales_data = await scraper.get_raw_sales(today, today)
            items = sales_data.get("data", [])
            print(f"Ventas encontradas hoy: {len(items)}")
            if items:
                print("Primer item de venta:", items[0].get("id"))
                detail = await scraper.get_sale_detail(items[0]["id"])
                print("Keys del detalle:", detail.get("data", {}).get("attributes", {}).keys())
        except Exception as e:
            print(f"Error: {e}")
            
    asyncio.run(test())
