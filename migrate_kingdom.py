from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

env_db_url = os.getenv("DATABASE_URL")
if env_db_url:
    if env_db_url.startswith("postgres://"):
        DATABASE_URL = env_db_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = env_db_url
else:
    DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(DATABASE_URL)

def migrate():
    print(f"Iniciando migración en: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    queries = [
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(20)",
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS birthdate TIMESTAMP WITHOUT TIME ZONE",
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS donde_nos_conocio VARCHAR(100)",
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0",
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS loyalty_level VARCHAR(20) DEFAULT 'bronze'",
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS stamps INTEGER DEFAULT 0",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_clientes_whatsapp ON clientes(whatsapp)"
    ]

    with engine.connect() as conn:
        for q in queries:
            try:
                print(f"Ejecutando: {q}")
                conn.execute(text(q))
                conn.commit()
            except Exception as e:
                print(f"Error o ya existe: {e}")

    print("Migración completada.")

if __name__ == "__main__":
    migrate()
