from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from . import models, database
from .routers import auth, ventas, stats, fudo, salon, billing

# Load environment variables from .env file
load_dotenv()

# Create tables automatically (for simple dev, usually we use alembic in prod)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Proyecto FOCUS API", version="0.1.0")

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(salon.router)
app.include_router(ventas.router)
app.include_router(stats.router)
app.include_router(billing.router)
app.include_router(fudo.router, prefix="/api/fudo", tags=["fudo"])

@app.get("/")
def read_root():
    return {"message": "Proyecto FOCUS Backend is running"}
