import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def create_table():
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    sql = """
    CREATE TABLE IF NOT EXISTS productos_fudo (
        id TEXT PRIMARY KEY,
        name TEXT,
        price DECIMAL(10,2),
        category_id TEXT,
        description TEXT,
        active BOOLEAN DEFAULT TRUE,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Habilitar RLS
    ALTER TABLE productos_fudo ENABLE ROW LEVEL SECURITY;
    
    -- Política para lectura pública
    CREATE POLICY "Public Read" ON productos_fudo FOR SELECT USING (true);
    """
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Supabase allows running SQL through the /pgrest/v1/rpc/exec_sql if configured, 
    # but usually we use the SQL editor. 
    # Since I don't have the SQL editor, I'll check if there's a table I can use
    # OR if I can just use the provided keys to create it via a migration-like approach if possible.
    # Actually, PostgREST doesn't allow DDL.
    
    print("Please run this SQL in your Supabase Dashboard:")
    print(sql)

if __name__ == "__main__":
    asyncio.run(create_table())
