import os
import httpx
from datetime import date
from typing import List, Dict, Any, Optional

class RukaClient:
    """
    Cliente para la API de Ruka.ai (Automatización de gastos).
    """
    def __init__(self, api_id: Optional[str] = None, api_key: Optional[str] = None, base_url: str = "https://app.ruka.ai/api/v1"):
        self.api_id = api_id or os.getenv("RUKA_API_ID")
        self.api_key = api_key or os.getenv("RUKA_API_KEY")
        self.base_url = base_url.rstrip("/")
        
    def get_headers(self) -> Dict[str, str]:
        if not self.api_key or not self.api_id:
            raise ValueError("RUKA_API_ID o RUKA_API_KEY no configuradas. Por favor agrégalas al archivo .env")
        return {
            "x-api-id": self.api_id,
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def fetch_purchases(self, desde: date, hasta: date) -> List[Dict[str, Any]]:
        """
        Obtiene las facturas de compra (DTEs recibidos) en un rango de fechas.
        """
        url = f"{self.base_url}/purchases"
        params = {
            "from_date": desde.isoformat(),
            "to_date": hasta.isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.get_headers(), params=params)
                if response.status_code == 200:
                    try:
                        return response.json().get("data", [])
                    except Exception:
                        print(f"Error: La API devolvió HTML en lugar de JSON. URL actual: {url}")
                        return []
                else:
                    print(f"Error Ruka API ({response.status_code}): {response.text[:200]}")
                    return []
            except Exception as e:
                print(f"Ruka connection error: {e}")
                return []

    async def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la validez de la API Key.
        """
        url = f"{self.base_url}/me" # Endpoint común para verificar auth
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.get_headers())
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "message": "Connection successful" if response.status_code == 200 else f"Error: {response.status_code}"
                }
            except Exception as e:
                return {"success": False, "message": str(e)}
