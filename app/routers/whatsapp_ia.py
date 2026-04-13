import os
import httpx
import logging
from fastapi import APIRouter, Request, BackgroundTasks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp IA"])

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "cPlq6mXKRR33wFhcOj4JrT3x7KB5aZxG")
WHAPI_URL = "https://gate.whapi.cloud"

@router.get("/webhook")
async def verify_webhook():
    """
    Permite la verificación del webhook por parte de Whapi.cloud u otros servicios.
    """
    return {"status": "ok", "message": "Kingdom Coffee Webhook is active"}

@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Recibe mensajes de WhatsApp desde Whapi.cloud
    """
    try:
        data = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}
    
    # Manejar solo mensajes entrantes (no ecos de nosotros mismos)
    messages = data.get("messages", [])
    for msg in messages:
        if msg.get("from_me") is True:
            continue
            
        chat_id = msg.get("chat_id") # e.g. "56912345678@s.whatsapp.net"
        text = msg.get("text", {}).get("body", "").lower()
        
        if text:
            background_tasks.add_task(process_ai_response, chat_id, text)
            
    return {"status": "ok"}

async def process_ai_response(chat_id: str, text: str):
    """
    Lógica de IA: Consultar Puntos, Menú y Reservas usando Gemini
    """
    from app.integrations.fudo_client import FudoClient
    from app.routers.ai import AIRequest
    import os
    try:
        from google import genai
    except ImportError:
        genai = None

    # 1. Obtener contexto de Fudo (Menú)
    fudo = FudoClient()
    products = await fudo.fetch_products()
    
    # Formatear menú para la IA (limitado para no saturar tokens)
    menu_text = "MENÚ KINGDOM COFFEE:\n"
    for p in products[:40]: # Tomamos los primeros 40 para eficiencia
        if p.get('active'):
            menu_text += f"- {p.get('name')}: ${p.get('price')}\n"

    # 2. Definir Contexto de la Cafetería
    contexto = f"""
    Eres el 'Mayordomo Real', el asistente virtual de Kingdom Coffee.
    TU PERSONALIDAD: Elegante, servicial, conocedor del café de especialidad. Hablas como un mayordomo moderno.
    
    INFORMACIÓN CLAVE:
    - Dirección: Av. Austral 1795, Puerto Montt.
    - Horarios: Lun-Vie 08:30-20:00, Sáb 09:30-19:00, Dom: Cerrado.
    - Especialidad: Café de especialidad y Tostaduría.
    - Bingo Real: Eventos especiales de Bingo en el local.
    
    {menu_text}
    
    INSTRUCCIONES:
    - Responde de forma autónoma basándote en el menú y horarios.
    - Si preguntan por puntos, diles que pronto podrán verlos directamente aquí, pero que por ahora usen la App.
    - Si quieren reservar, diles que elijan su mesa en la App y el sistema me avisará para confirmarla.
    - Sé breve y amable.
    """

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or not genai:
        # Fallback si no hay IA
        response_text = "¡Hola! ☕ Soy el Mayordomo de Kingdom Coffee. Recibí tu mensaje: '" + text + "'. En este momento mi 'cerebro' está descansando, pero pronto podré responderte todo sobre nuestro menú y horarios."
    else:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"{contexto}\n\nCliente dice: {text}\nMayordomo Real responde:"
            
            response = client.models.generate_content(
                model='gemini-1.5-flash', contents=prompt
            )
            response_text = response.text.strip()
        except Exception as e:
            logger.error(f"Error en Gemini WhatsApp: {str(e)}")
            response_text = "¡Hola! Una disculpa, mi conexión real está algo inestable. ¿Podrías repetirme eso?"

    if response_text:
        await send_whatsapp(chat_id, response_text)

async def send_whatsapp(chat_id: str, text: str):
    url = f"{WHAPI_URL}/messages/text"
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "typing_time": 2,
        "to": chat_id,
        "body": text
    }
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {str(e)}")
