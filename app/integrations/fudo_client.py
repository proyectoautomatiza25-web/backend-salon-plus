import httpx
import base64
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno al inicio
load_dotenv()

logger = logging.getLogger(__name__)

class FudoClient:
    """
    Cliente asíncrono para integración con la API de Fudo.
    Soporta tanto Basic Auth (API de Aplicaciones) como Bearer Auth (Token de sesión).
    """
    def __init__(self):
        # Limpiar variables de entorno por si Vercel inyecta retornos de carro
        base = os.getenv("FUDO_BASE_URL", "https://api.fu.do")
        if base: base = base.strip().replace("\n", "").replace("\r", "")
        self.base_url = base.rstrip('/')
        
        c_id = os.getenv("FUDO_CLIENT_ID")
        self.client_id = c_id.strip().replace("\n", "").replace("\r", "") if c_id else None
        
        c_sec = os.getenv("FUDO_CLIENT_SECRET")
        self.client_secret = c_sec.strip().replace("\n", "").replace("\r", "") if c_sec else None
        
        b_tok = os.getenv("FUDO_BEARER_TOKEN")
        self.bearer_token = b_tok.strip().replace("\n", "").replace("\r", "") if b_tok else None
    async def refresh_token(self):
        """Obtiene un nuevo Bearer Token usando Client ID/Secret"""
        if not self.client_id or not self.client_secret:
            logger.warning("FUDO_CLIENT_ID o FUDO_CLIENT_SECRET no configurados.")
            return None
        
        url = "https://auth.fu.do/api"
        payload = {"apiKey": self.client_id, "apiSecret": self.client_secret}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=payload, headers=headers, timeout=10.0)
                if r.status_code == 200:
                    new_token = r.json().get("token")
                    if new_token:
                        self.bearer_token = new_token
                        logger.info("Fudo Bearer Token refrescado con éxito.")
                        return new_token
                else:
                    logger.error(f"Error refrescando token Fudo: {r.status_code} - {r.text}")
        except Exception as e:
            logger.error(f"Excepción al refrescar token Fudo: {e}")
        
        return None

    def get_auth_headers(self) -> dict:
        """
        Genera los headers de autenticación. Prioriza Bearer Token si existe.
        """
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://app-v2.fu.do",
            "Referer": "https://app-v2.fu.do/",
            "fudo-country-code": "CL"
        }

        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.client_id and self.client_secret:
            token = f"{self.client_id}:{self.client_secret}"
            token_b64 = base64.b64encode(token.encode()).decode()
            headers["Authorization"] = f"Basic {token_b64}"
        
        return headers
    
    async def fetch_orders(self, desde: datetime, hasta: datetime) -> List[Dict]:
        """
        Obtiene las órdenes/ventas de Fudo usando parámetros de tiempo precisos.
        """
        headers = self.get_auth_headers()
        
        # Fudo API a veces prefiere 'from' y 'to' en formato ISO con T o solo fecha
        params = {"per_page": 100}
        if desde:
            params["from"] = desde.strftime("%Y-%m-%dT%H:%M:%S") if isinstance(desde, datetime) else desde.isoformat()
        if hasta:
            params["to"] = hasta.strftime("%Y-%m-%dT%H:%M:%S") if isinstance(hasta, datetime) else hasta.isoformat()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Intentar /sales (Estándar con filtros)
            try:
                r = await client.get(f"{self.base_url}/sales", headers=headers, params=params)
                if r.status_code == 200:
                    data = r.json()
                    results = []
                    if isinstance(data, dict):
                        results = data.get("data", list(data.values()))
                    elif isinstance(data, list):
                        results = data
                    
                    # Convertir a lista de dicts y ordenar por fecha (descendente)
                    orders = [s for s in results if isinstance(s, dict)]
                    # Intentar ordenar por createdAt si existe
                    try:
                        orders.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
                    except: pass
                    return orders
            except Exception as e:
                logger.error(f"Fudo API /sales error: {e}")

    async def fetch_order_by_number(self, ticket_number: str) -> Optional[Dict]:
        """Busca una orden específica por su número de ticket/folio."""
        headers = self.get_auth_headers()
        # Buscamos en las órdenes más recientes sin filtros de fecha para máxima velocidad
        orders = await self.fetch_orders(None, None)
        for o in orders:
            # Revisar número directo
            if str(o.get('number')) == str(ticket_number):
                return o
            # Revisar en saleReceipts
            receipts = o.get('saleReceipts', [])
            for r in receipts:
                if str(r.get('number')) == str(ticket_number):
                    return o
        return None

    async def fetch_bills(self, desde: date, hasta: date) -> List[Dict]:
        """Obtiene facturas/boletas generadas."""
        endpoint = f"{self.base_url}/bills"
        params = {"from": desde.isoformat(), "to": hasta.isoformat()}
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(endpoint, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                return []
        except: return []

    async def fetch_guest(self, guest_id: str) -> Optional[Dict]:
        """Obtiene detalle de un cliente en Fudo."""
        endpoint = f"{self.base_url}/guests/{guest_id}"
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(endpoint, headers=headers)
                return r.json() if r.status_code == 200 else None
        except: return None
    
    async def fetch_products(self) -> List[Dict]:
        endpoint = f"{self.base_url}/products"
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, headers=headers)
                
                # Retry once if 401
                if response.status_code == 401:
                    await self.refresh_token()
                    response = await client.get(endpoint, headers=self.get_auth_headers())
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Fudo API response type for products: {type(data)}")
                
                # Normalizar: Fudo puede devolver una lista, o un dict con 'data' o un dict de IDs
                results = []
                if isinstance(data, list):
                    results = data
                elif isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        results = data['data']
                    else:
                        # Si es un dict de {id: {prod}}, convertimos a lista
                        results = list(data.values())
                
                # Asegurar que cada item es un dict
                return [p for p in results if isinstance(p, dict)]
        except Exception as e:
            logger.error(f"Error fetching Fudo products: {str(e)}")
            return []

    async def fetch_tables(self) -> List[Dict]:
        endpoint = f"{self.base_url}/tables"
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(endpoint, headers=headers)
                if response.status_code == 401:
                    await self.refresh_token()
                    response = await client.get(endpoint, headers=self.get_auth_headers())
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict): return list(data.values())
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error fetching Fudo tables: {str(e)}")
            return []

    async def fetch_categories(self) -> List[Dict]:
        endpoint = f"{self.base_url}/product_categories"
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(endpoint, headers=headers)
                if response.status_code == 401:
                    await self.refresh_token()
                    response = await client.get(endpoint, headers=self.get_auth_headers())
                response.raise_for_status()
                data = response.json()
                
                results = []
                if isinstance(data, list):
                    results = data
                elif isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        results = data['data']
                    else:
                        results = list(data.values())
                
                return [c for c in results if isinstance(c, dict)]
        except Exception as e:
            logger.error(f"Error fetching Fudo categories: {str(e)}")
            return []
    
    async def fetch_reservations(self, desde: date, hasta: date) -> List[Dict]:
        endpoint = f"{self.base_url}/reservations"
        params = {
            "from": desde.isoformat(),
            "to": hasta.isoformat()
        }
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(endpoint, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict): return data.get('data', [])
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error fetching Fudo reservations: {str(e)}")
            return []

    async def create_reservation(self, reservation_data: Dict) -> Dict:
        endpoint = f"{self.base_url}/reservations"
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(endpoint, headers=headers, json=reservation_data)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Error creating Fudo reservation: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def create_sale(self, sale_data: Dict) -> Dict:
        """
        Crea una nueva venta/pedido en Fudo.
        sale_data debe seguir el esquema de Fudo (items, customer, etc.)
        """
        endpoint = f"{self.base_url}/sales"
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, headers=headers, json=sale_data)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Error creating Fudo sale: {str(e)}")
            return {"success": False, "message": str(e)}

    async def fetch_providers(self) -> List[Dict]:
        """Obtiene la lista de proveedores de Fudo."""
        endpoint = f"{self.base_url}/providers"
        headers = self.get_auth_headers()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(endpoint, headers=headers)
                if response.status_code == 401:
                    await self.refresh_token()
                    response = await client.get(endpoint, headers=self.get_auth_headers())
                response.raise_for_status()
                data = response.json()
                
                results = []
                if isinstance(data, list):
                    results = data
                elif isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        results = data['data']
                    else:
                        results = list(data.values())
                
                return [p for p in results if isinstance(p, dict)]
        except Exception as e:
            logger.error(f"Error fetching Fudo providers: {str(e)}")
            return []

    async def test_connection(self) -> Dict:
        try:
            # Usamos /products para testear ya que dio 200 con el token
            endpoint = f"{self.base_url}/products"
            headers = self.get_auth_headers()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(endpoint, headers=headers)
                
                # Auto-recuperación si el token guardado expiró (401)
                if response.status_code == 401:
                    logger.info("Token expirado en test_connection. Intentando refresh...")
                    new_token = await self.refresh_token()
                    if new_token:
                        response = await client.get(endpoint, headers=self.get_auth_headers())
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "message": "Conectado a Fudo correctamente" if response.status_code == 200 else f"Error de conexión: {response.status_code}"
            }
        except Exception as e:
            logger.error(f"Fallo crítico en test_connection: {e}")
            return {"success": False, "message": f"Fallo crítico: {str(e)}"}
