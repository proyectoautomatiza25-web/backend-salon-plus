import httpx
import asyncio

async def test_geofence():
    url = "https://backend-salon-plus.vercel.app/api/kingdom/geofence-trigger"
    payload = {
        "user_id": "broadcast",
        "user_email": "",
        "distance_meters": 0,
        "bonus_crowns": 50,
        "custom_message": "¡Esta es una prueba de Geofencing y Marketing para Kingdom Coffee!",
        "is_campaign": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_geofence())
