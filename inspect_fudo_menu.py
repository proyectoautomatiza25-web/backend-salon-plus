import os, httpx, asyncio, json
from dotenv import load_dotenv

load_dotenv("c:/Users/Lenovo/clod database/backend-salon-plus/.env")

async def test():
    token = os.getenv("FUDO_BEARER_TOKEN")
    base_url = os.getenv("FUDO_BASE_URL", "https://api.fu.do").rstrip('/')
    headers = {
        "Authorization": f"Bearer {token}",
        "fudo-country-code": "CL",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        # Categorías
        r_cat = await client.get(f"{base_url}/product_categories", headers=headers)
        print("=== CATEGORÍAS ===")
        print(json.dumps(r_cat.json(), indent=2))
        
        # Productos (limitamos a 10 para ver estructura)
        r_prod = await client.get(f"{base_url}/products", headers=headers)
        print("\n=== PRODUCTOS (primeros 5) ===")
        data = r_prod.json()
        prods = list(data.values()) if isinstance(data, dict) else data
        print(json.dumps(prods[:5], indent=2))

if __name__ == "__main__":
    asyncio.run(test())
