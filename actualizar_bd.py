from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Usando la URL de la base de datos de producción (Kingdom Coffee) vía Pooler
DATABASE_URL = "postgresql://postgres.bcfulknkkwlpxpiuboyt:FLORENCIA2010JULIETA2022@aws-0-us-west-2.pooler.supabase.com:6543/postgres?sslmode=require"

def fix_schema():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("🔍 Verificando columnas en 'ventas_fudo'...")
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'ventas_fudo'"))
        columns = [r[0] for r in res]
        print(f"Columnas actuales: {columns}")
        
        if 'conceptos' not in columns:
            print("➕ Agregando columna 'conceptos'...")
            conn.execute(text("ALTER TABLE ventas_fudo ADD COLUMN conceptos TEXT;"))
        
        if 'origen' not in columns:
            print("➕ Agregando columna 'origen'...")
            conn.execute(text("ALTER TABLE ventas_fudo ADD COLUMN origen TEXT DEFAULT 'POS';"))
            
        print("🔍 Verificando tabla 'facturas_fudo'...")
        res = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'facturas_fudo');"))
        if not res.scalar():
            print("🚀 Creando tabla 'facturas_fudo'...")
            conn.execute(text("""
                CREATE TABLE facturas_fudo (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    fudo_bill_id TEXT UNIQUE,
                    tipo TEXT,
                    numero TEXT,
                    monto NUMERIC(14,2),
                    fecha TIMESTAMP WITH TIME ZONE,
                    cliente_nombre TEXT,
                    sale_id TEXT,
                    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
        else:
            print("✅ La tabla 'facturas_fudo' ya existe.")
            
        conn.commit()
        print("✨ Proceso completado.")

if __name__ == "__main__":
    fix_schema()
