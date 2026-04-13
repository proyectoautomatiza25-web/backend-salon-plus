const { Client } = require('pg');
require('dotenv').config();

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const connectionString = "postgresql://postgres.bcfulknkkwlpxpiuboyt:FLORENCIA2010JULIETA2022@aws-0-us-west-2.pooler.supabase.com:6543/postgres?sslmode=require";

async function createTable() {
  const client = new Client({
    connectionString: connectionString,
    ssl: {
      rejectUnauthorized: false
    }
  });

  try {
    await client.connect();
    console.log("Connected to Supabase PostgreSQL.");

    const sql = `
    CREATE TABLE IF NOT EXISTS public.geofence_events (
        id SERIAL PRIMARY KEY,
        user_id TEXT,
        user_email TEXT,
        distance_meters INTEGER,
        bonus_crowns INTEGER,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        location TEXT
    );

    ALTER TABLE public.geofence_events ENABLE ROW LEVEL SECURITY;
    
    DROP POLICY IF EXISTS "service_role_all" ON public.geofence_events;
    CREATE POLICY "service_role_all" ON public.geofence_events FOR ALL USING (true);
    `;

    await client.query(sql);
    console.log("Successfully created geofence_events table.");
  } catch (err) {
    console.error("Error creating table:", err);
  } finally {
    await client.end();
  }
}

createTable();
