import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Path fixing for backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

DATABASE_URL = "postgresql://postgres:FLORENCIA2010JULIETA2022@db.bcfulknkkwlpxpiuboyt.supabase.co:5432/postgres"

def run_migration():
    if not DATABASE_URL:
        print("❌ Error: No DATABASE_URL found.")
        return

    engine = create_engine(DATABASE_URL)
    
    sql = """
    -- Tabla para el Menú completo de Fudo
    CREATE TABLE IF NOT EXISTS public.productos_fudo (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        price DECIMAL(10,2),
        category_id TEXT,
        description TEXT,
        active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Habilitar RLS
    ALTER TABLE public.productos_fudo ENABLE ROW LEVEL SECURITY;

    -- Política de lectura pública
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_policy WHERE polname = 'Public read access' AND polrelid = 'public.productos_fudo'::regclass) THEN
            CREATE POLICY "Public read access" ON public.productos_fudo FOR SELECT USING (true);
        END IF;
    END $$;

    -- Política de gestión para el sistema
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_policy WHERE polname = 'Service manages all' AND polrelid = 'public.productos_fudo'::regclass) THEN
            CREATE POLICY "Service manages all" ON public.productos_fudo FOR ALL USING (true);
        END IF;
    END $$;
    """
    
    print("🚀 Ejecutando migración para productos_fudo...")
    try:
        with engine.connect() as conn:
            # Dividir por ; para ejecutar varias sentencias si es necesario, 
            # pero SQLAlchemy suele manejar bloques si se envuelven correctamente
            conn.execute(text(sql))
            conn.commit()
        print("✅ Migración completada con éxito.")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    run_migration()
