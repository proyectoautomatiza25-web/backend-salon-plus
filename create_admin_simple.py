#!/usr/bin/env python3
"""
Script simple para crear usuario admin
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import Base, User
from passlib.context import CryptContext

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_admin():
    db = SessionLocal()
    
    try:
        # Credenciales predefinidas
        email = "admin@agendaplus.cl"
        password = "admin123"
        
        # Verificar si existe
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"✅ Usuario ya existe:")
            print(f"   📧 Email: {email}")
            print(f"   🔑 Password: {password}")
            print(f"   🆔 ID: {existing.id}")
            return existing
        
        # Crear nuevo
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            business_name="Centro Médico Agenda Plus",
            plan_type="demo",
            trial_start_at=datetime.utcnow(),
            trial_end_at=datetime.utcnow() + timedelta(days=30),
            subscription_active=True,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("✅ Usuario ADMIN creado exitosamente!")
        print(f"   📧 Email: {email}")
        print(f"   🔑 Password: {password}")
        print(f"   🆔 ID: {new_user.id}")
        print(f"   📅 Trial hasta: {new_user.trial_end_at.strftime('%Y-%m-%d')}")
        print()
        print("🚀 Accede en: http://localhost:5173/")
        
        return new_user
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  CREAR USUARIO ADMIN - AGENDA PLUS")
    print("=" * 60)
    print()
    create_admin()
