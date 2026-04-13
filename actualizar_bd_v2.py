import psycopg2
import os

# Usando la URL de la base de datos de producción (Kingdom Coffee) vía Direct Port
DATABASE_URL = "postgresql://postgres:FLORENCIA2010JULIETA2022@db.bcfulknkkwlpxpiuboyt.supabase.co:5432/postgres?sslmode=require"

def fix_schema():
    try:
        print("🔍 Conectando a la base de datos...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🔍 Verificando columnas en 'ventas_fudo'...")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'ventas_fudo'")
        columns = [r[0] for r in cur.fetchall()]
        print(f"Columnas actuales: {columns}")
        
        if 'conceptos' not in columns:
            print("➕ Agregando columna 'conceptos'...")
            cur.execute("ALTER TABLE ventas_fudo ADD COLUMN conceptos TEXT;")
        
        if 'origen' not in columns:
            print("➕ Agregando columna 'origen'...")
            cur.execute("ALTER TABLE ventas_fudo ADD COLUMN origen TEXT DEFAULT 'POS';")

        if 'cliente_email' not in columns:
            print("➕ Agregando columna 'cliente_email'...")
            cur.execute("ALTER TABLE ventas_fudo ADD COLUMN cliente_email TEXT;")
            
        print("🔍 Verificando tabla 'facturas_fudo'...")
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'facturas_fudo');")
        if not cur.fetchone()[0]:
            print("🚀 Creando tabla 'facturas_fudo'...")
            cur.execute("""
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
            """)
        else:
            print("✅ La tabla 'facturas_fudo' ya existe.")
            
        cur.close()
        conn.close()
        print("✨ Proceso completado.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    fix_schema()
