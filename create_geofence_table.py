from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv('.env.production')

# Fallback in case env loading fails
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres.wnzpltxackalafxrbeix:FLORENCIA2010JULIETA2022@aws-0-us-west-2.pooler.supabase.com:6543/postgres")

sql_statements = [
    """
    CREATE TABLE IF NOT EXISTS public.geofence_events (
        id SERIAL PRIMARY KEY,
        user_id TEXT,
        user_email TEXT,
        distance_meters INTEGER,
        bonus_crowns INTEGER,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        location TEXT
    );
    """,
    "ALTER TABLE public.geofence_events ENABLE ROW LEVEL SECURITY;",
    "DROP POLICY IF EXISTS \"service_role_all\" ON public.geofence_events;",
    "CREATE POLICY \"service_role_all\" ON public.geofence_events FOR ALL USING (true);"
]

def create_table():
    try:
        # We need to make sure the URL is compatible with SQLAlchemy if it's using the postgresql:// scheme
        engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))
        with engine.connect() as conn:
            for sql in sql_statements:
                print(f"Executing: {sql.strip()[:50]}...")
                conn.execute(text(sql))
            conn.commit()
            print("Successfully created geofence_events table and policies.")
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()
