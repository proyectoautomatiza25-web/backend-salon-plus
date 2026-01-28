import httpx
import base64
from datetime import date
from typing import List, Dict
import logging
import os

logger = logging.getLogger(__name__)


class FudoClient:
    """
    Cliente asíncrono para integración con la API de Fudo.
    
    Usa las credenciales de "Aplicaciones Externas (beta)" de Fudo
    para autenticar y obtener datos de órdenes/ventas.
    """
    
    def __init__(self):
        """
        Inicializa el cliente Fudo leyendo variables de entorno.
        
        Variables requeridas:
        - FUDO_BASE_URL: URL base de la API de Fudo
        - FUDO_CLIENT_ID: Client ID de Aplicaciones Externas
        - FUDO_CLIENT_SECRET: Client Secret de Aplicaciones Externas
        """
        self.base_url = os.getenv("FUDO_BASE_URL", "https://app-v2.fu.do").rstrip('/')
        self.client_id = os.getenv("FUDO_CLIENT_ID")
        self.client_secret = os.getenv("FUDO_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("FUDO_CLIENT_ID and FUDO_CLIENT_SECRET must be set in environment")
        
    def get_auth_headers(self) -> dict:
        """
        Genera los headers de autenticación para las peticiones a Fudo.
        
        Usa Basic Auth con client_id:client_secret codificado en base64.
        
        Returns:
            dict: Headers con autenticación
        """
        # Formato Basic Auth: "client_id:client_secret" en base64
        token = f"{self.client_id}:{self.client_secret}"
        token_b64 = base64.b64encode(token.encode()).decode()
        
        return {
            "Authorization": f"Basic {token_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ProyectoFOCUS/1.0"
        }
    
    async def fetch_orders(self, desde: date, hasta: date) -> List[Dict]:
        """
        Obtiene las órdenes/ventas de Fudo en un rango de fechas (async).
        
        Args:
            desde: Fecha de inicio (YYYY-MM-DD)
            hasta: Fecha de fin (YYYY-MM-DD)
            
        Returns:
            list: Lista de órdenes en formato JSON
            
        Raises:
            httpx.HTTPError: Si la petición falla
            ValueError: Si la respuesta no es válida
        """
        endpoint = f"{self.base_url}/api/integrations/orders"
        
        params = {
            "from": desde.isoformat(),
            "to": hasta.isoformat()
        }
        
        headers = self.get_auth_headers()
        
        try:
            logger.info(f"Fetching Fudo orders from {desde} to {hasta}")
            logger.debug(f"Request URL: {endpoint}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    endpoint,
                    headers=headers,
                    params=params
                )
            
            logger.info(f"Fudo API response status: {response.status_code}")
            
            # Si no es exitoso, lanzar excepción
            if response.status_code != 200:
                logger.error(f"Fudo API error: {response.text}")
                response.raise_for_status()
            
            data = response.json()
            
            # Validar que sea una lista
            if not isinstance(data, list):
                # Algunas APIs envuelven la lista en un objeto
                if isinstance(data, dict):
                    data = data.get('orders') or data.get('results') or data.get('data') or []
                else:
                    raise ValueError(f"Unexpected response format: {type(data)}")
            
            logger.info(f"Successfully fetched {len(data)} orders from Fudo")
            return data
            
        except httpx.TimeoutException:
            logger.error("Fudo API request timed out")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Fudo API request failed: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Invalid Fudo API response: {str(e)}")
            raise
    
    async def fetch_products(self) -> List[Dict]:
        """
        Obtiene el catálogo de productos de Fudo (async).
        
        Returns:
            list: Lista de productos
        """
        endpoint = f"{self.base_url}/api/integrations/products"
        headers = self.get_auth_headers()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching Fudo products: {str(e)}")
            raise
    
    async def test_connection(self) -> Dict:
        """
        Prueba la conexión con la API de Fudo (async).
        
        Returns:
            dict: Información sobre el estado de la conexión
        """
        try:
            endpoint = f"{self.base_url}/api/integrations/status"
            headers = self.get_auth_headers()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(endpoint, headers=headers)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "message": "Connection successful" if response.status_code == 200 else f"Error: {response.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "message": f"Connection failed: {str(e)}"
            }
