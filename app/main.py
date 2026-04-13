import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Path fixing for Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from . import models, database
from .routers import auth, ventas, stats, fudo, salon, billing, ai, ruka, public, kingdom, whatsapp_ia, marketing
from .config_loader import apply_config

# Load env & config
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)
apply_config()

app = FastAPI(title="Kingdom Coffee API", version="1.1.6")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(salon.router)
app.include_router(ventas.router)
app.include_router(stats.router)
app.include_router(billing.router)
app.include_router(ai.router)
app.include_router(fudo.router, prefix="/api/fudo", tags=["fudo"])
app.include_router(ruka.router, prefix="/api/ruka", tags=["ruka"])
app.include_router(kingdom.router)
app.include_router(whatsapp_ia.router)
app.include_router(public.router)
app.include_router(marketing.router)

@app.get("/")
def read_root():
    return {"message": "Kingdom Coffee Backend is ONLINE", "status": "perfect", "version": "1.1.6"}

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.1.6"}
