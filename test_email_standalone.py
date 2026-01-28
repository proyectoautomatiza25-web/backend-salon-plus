from app.services.email_service import send_welcome_email
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Email Sending...")
print(f"Host: {os.getenv('SMTP_HOST')}")
print(f"User: {os.getenv('SMTP_USER')}")

try:
    success = send_welcome_email("mauricio31121983@gmail.com")
    if success:
        print("✅ Email Sent Successfully!")
    else:
        print("❌ Email Failed (Check logs in email_service)")
except Exception as e:
    print(f"❌ Exception: {e}")
