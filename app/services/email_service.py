import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def send_email(to_email: str, subject: str, body: str):
    """
    Sends an email using the SMTP configuration.
    """
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL]):
        logger.warning("SMTP configuration missing. Email not sent.")
        # For development, just log
        print(f"--- FAKE EMAIL SENT TO {to_email} ---\nSubject: {subject}\n{body}\n----------------------------------")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
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
            <a href="http://localhost:5173" style="background-color: #F472B6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Acceder a mi Cuenta</a>
            <br/><br/>
            <p>Saludos,<br/>El Equipo de Salon Plus by Automatiza Sur</p>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)
