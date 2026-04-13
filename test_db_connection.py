from sqlalchemy import create_engine, text

# URL encontrada en tu código
DATABASE_URL = "postgresql://postgres.wnzpltxackalafxrbeix:FLORENCIA2010JULIETA2022@aws-0-us-west-2.pooler.supabase.com:6543/postgres"

print("--- PROBANDO CONEXIÓN A SUPABASE ---")
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ CONEXIÓN EXITOSA!")
except Exception as e:
    print(f"❌ FALLÓ LA CONEXIÓN: {e}")
