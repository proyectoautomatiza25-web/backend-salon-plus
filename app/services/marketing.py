import os
import logging
import httpx

logger = logging.getLogger(__name__)

# API de Brevo (Mucho más fiable que SMTP para Vercel)
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "").strip()
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "automatizakingdomcoffee@gmail.com").strip()

class MarketingService:
    SMTP_HOST_STR = "api.brevo.com (HTTP)"
    SMTP_USER_STR = SENDER_EMAIL
    SMTP_PASSWORD_SET = bool(BREVO_API_KEY)

    @staticmethod
    def send_email(to_email, subject, content_html):
        """Envía un corre electrónico via Brevo API. Retorna (success, error_msg)"""
        if not BREVO_API_KEY:
            return False, "BREVO_API_KEY no configurada"

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": BREVO_API_KEY
        }
        
        payload = {
            "sender": {"name": "KINGDOM COFFEE", "email": SENDER_EMAIL},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": content_html
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, json=payload)
                resp_json = response.json() if "application/json" in response.headers.get("Content-Type", "") else {"text": response.text}
                
                if response.status_code in [200, 201, 202]:
                    msg_id = resp_json.get("messageId")
                    logger.info(f"Email enviado via Brevo a {to_email}. ID: {msg_id}")
                    return True, f"OK - ID: {msg_id}"
                else:
                    logger.error(f"Error Brevo API ({response.status_code}): {resp_json}")
                    return False, f"Brevo API Error {response.status_code}: {resp_json}"
        except Exception as e:
            logger.error(f"Excepción enviando via Brevo a {to_email}: {str(e)}")
            return False, str(e)

    @staticmethod
    async def blast_campaign(subject, template_name, clients, custom_body=None):
        """Envía una campaña a una lista de clientes."""
        success_count = 0
        
        def get_styled_html(body_content):
            return f"""
            <html>
            <body style="background-color: #000; color: #fff; font-family: 'Helvetica', sans-serif; padding: 40px; text-align: center;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #333; border-radius: 30px; overflow: hidden; background: #080808; padding: 40px;">
                    <h1 style="color: #f59e0b; font-size: 32px; letter-spacing: -1px; margin-bottom: 20px; font-style: italic;">KINGDOM <span style="color: #fff;">COFFEE</span></h1>
                    <div style="text-align: left; line-height: 1.6; font-size: 16px;">
                        {body_content}
                    </div>
                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #222; font-size: 12px; color: #555; text-transform: uppercase; letter-spacing: 2px;">
                        Fusión de Arte y Café • Salon Plus Experience
                    </div>
                </div>
            </body>
            </html>
            """

        templates = {
            "welcome": get_styled_html("""
                <h2 style="color: #fff; margin-bottom: 20px;">¡BIENVENIDO AL REINO! ☕</h2>
                <p>Tu viaje sensorial ha comenzado. A partir de ahora, eres parte de la élite de <b>Kingdom Coffee</b>.</p>
                <p>Disfruta de beneficios exclusivos, puntos por cada sorbo y acceso anticipado a nuestros eventos más exclusivos.</p>
                <p style="background: #f59e0b; color: #000; padding: 15px; display: inline-block; border-radius: 12px; font-weight: 800; margin-top: 20px;">USA TU QR EN CAJA PARA SUMAR PUNTOS</p>
            """),
            "promotion": get_styled_html("""
                <h2 style="color: #fff; margin-bottom: 20px;">UNA OFERTA DIGNA DE REALEZA ✨</h2>
                <p>Hoy el Kingdom te consiente. Pasa por tu café favorito y obtén un <b>20% de descuento</b> automático al mostrar este correo.</p>
                <p>Nuestros baristas te esperan para elevar tu experiencia.</p>
                <p style="color: #f59e0b; font-size: 12px; margin-top: 20px;">*Válido solo por hoy en nuestro local oficial.</p>
            """)
        }
        
        if template_name == 'custom' and custom_body:
            content = get_styled_html(custom_body)
        else:
            content = templates.get(template_name, get_styled_html("<p>Tenemos novedades en el Reino que no querrás perderte.</p>"))
        
        for client in clients:
            email = client.get('email')
            if email and "@" in email:
                success, _ = MarketingService.send_email(email, subject, content)
                if success:
                    success_count += 1
                    
        return success_count
