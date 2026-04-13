from sqlalchemy import create_engine, text
import os

DATABASE_URL = "postgresql://postgres:FLORENCIA2010JULIETA2022@db.bcfulknkkwlpxpiuboyt.supabase.co:5432/postgres"

def check_schema():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'productos_fudo'"))
        columns = [r[0] for r in res]
        print(f"Columns in productos_fudo: {columns}")
        
        # Also check current entries
        res = conn.execute(text("SELECT COUNT(*) FROM productos_fudo"))
        count = res.scalar()
        print(f"Total entries: {count}")

if __name__ == "__main__":
    check_schema()
