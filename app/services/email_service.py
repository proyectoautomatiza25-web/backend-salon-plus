import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT_STR = os.getenv("SMTP_PORT", "587").strip()
SMTP_PORT = int(SMTP_PORT_STR) if SMTP_PORT_STR.isdigit() else 587
SMTP_USER = os.getenv("SMTP_USER", "automatizakingdomcoffee@gmail.com").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "automatizakingdomcoffee@gmail.com").strip()

def send_email(to_email: str, subject: str, body: str):
    """
    Sends an email using the SMTP settings (Gmail).
    """
    if not SMTP_PASSWORD:
        logger.warning("SMTP_PASSWORD missing. Email not sent.")
        print(f"--- FAKE EMAIL SENT TO {to_email} ---\nSubject: {subject}\n{body}\n----------------------------------")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = f"KINGDOM COFFEE <{SENDER_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        # Si el body tiene HTML, lo adjuntamos como HTML
        if "<html>" in body or "<div" in body:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Error sending SMTP email to {to_email}: {str(e)}")
        return False

def send_welcome_email(to_email: str):
    subject = "¡Bienvenido a Salon Plus!"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #F472B6;">Bienvenido a Salon Plus ✨</h2>
            <p>Hola,</p>
            <p>Gracias por registrarte en la plataforma líder para gestión de salones de belleza y barberías.</p>
            <p>Estamos emocionados de ayudarte a llevar tu negocio al siguiente nivel.</p>
            <br/>
            <br/>
            <p>Accede a tu cuenta aquí:</p>
            <a href="https://salonplus.automatizasur.cl" style="background-color: #F472B6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Ingresar a Salon Plus</a>
            <br/><br/>
            <p>Saludos,<br/>El Equipo de Salon Plus by Automatiza Sur</p>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)
