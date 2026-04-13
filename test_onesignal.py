import httpx
import asyncio

async def send_direct_push():
    app_id = "acb5b8b3-4417-4056-91f0-bc6cc8e1cdf4"
    api_key = "os_v2_app_vs23rm2ec5afnepqxrwmryon6sz7waqk252ufknesivugbvlpeyhofbt2tdjswethaumvreggd7hye4qj2qu2732hcftk3avjhhmkry"
    
    url = "https://onesignal.com/api/v1/notifications"
    
    headers = {
        "Authorization": f"Basic {api_key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    payload = {
        "app_id": app_id,
        "included_segments": ["Subscribed Users"],
        "contents": {"en": "¡Notificación de prueba directa! Si ves esto, tu teléfono está recibiendo notificaciones correctly de Kingdom Coffee 🚀", "es": "¡Notificación de prueba directa! Si ves esto, tu teléfono está recibiendo notificaciones correctamente de Kingdom Coffee 🚀"},
        "headings": {"en": "👑 Alerta Kingdom Coffee", "es": "👑 Alerta Kingdom Coffee"}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")

if __name__ == "__main__":
    asyncio.run(send_direct_push())
