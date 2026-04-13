import os

# Definición de variables para entorno Vercel (cuando el Dashboard no las tiene)
CONFIG = {
    "FUDO_BASE_URL": "https://api.fu.do",
    "FUDO_CLIENT_ID": "MzZAMTkxNDcz",
    "FUDO_CLIENT_SECRET": "Wj64Cp9e3SAEAYesMEADneS3hMj6WQfC",
    "DATABASE_URL": "postgresql://postgres.bcfulknkkwlpxpiuboyt:FLORENCIA2010JULIETA2022@aws-0-us-west-2.pooler.supabase.com:6543/postgres",
    "JWT_SECRET": "dev_secret_change_in_production",
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "SMTP_USER": "contacto@automatizasur.cl",
    "SMTP_PASSWORD": "iwqe xmng rari zqhu",
    "SENDER_EMAIL": "contacto@automatizasur.cl",
    "MP_ACCESS_TOKEN": "TEST-6703285773653661-012801-c9c03ce8a2bfda961701efaca8b49025-3164912896",
    "MP_PLAN_ID": "f9f6fb0ec30d41ecbe6b18ea75f8ecd9",
    "FRONTEND_URL": "https://salonplus.automatizasur.cl",
    "FLOW_API_KEY": "59657FBA-0397-444D-A320-9C61FC02BL8B",
    "FLOW_SECRET_KEY": "797e6007aabb3701b1ebe13c2e453fc9571ae4f6",
    "GOOGLE_API_KEY": "AIzaSyDLVlaWC_z2DvFVBL9DhgsfFfAz335Adzw",
    "RUKA_API_ID": "a4f92c1e7b6d4a0a6c83f1d2b5e67890",
    "RUKA_API_KEY": "f18c3d4a0b9e8625d1e7c890e2b654ff",
    "FUDO_BEARER_TOKEN": "eyJhbGciOiJIUzI1NiJ9.eyJhaSI6MTkxNDczLCJ1aSI6MzYsImV4cCI6MTc3MDg2Njg0MX0.QtDb4t3v5SLP9jXTEGOJegSBhegc7a34dya_VgPDdek"
}

def apply_config():
    """Aplica las variables al entorno de ejecución si no están presentes."""
    for key, value in CONFIG.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"DEBUG: Setting {key} from config_loader")
