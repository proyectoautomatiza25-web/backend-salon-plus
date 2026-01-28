import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
url = os.getenv("DATABASE_URL")
# Hide password in log
print(f"Connecting to DB...") 

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT version()"))
        version = res.fetchone()
        print(f"✅ SUCCESS! Connected to: {version[0]}")
except Exception as e:
    print(f"❌ FAILED: {e}")
