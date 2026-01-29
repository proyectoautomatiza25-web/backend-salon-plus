#!/usr/bin/env python3
"""
Script para crear un usuario de prueba con trial de 7 días
"""
import sys
import os
from datetime import datetime, timedelta

# Agregar el path del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def create_test_user(email: str, password: str):
    """Crea un usuario de prueba con trial activo"""
    db = SessionLocal()
    
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ El usuario {email} ya existe.")
            print(f"   Puedes usar otro email o eliminar el usuario existente.")
            return None
        
        # Crear nuevo usuario
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            business_name="Salon de Prueba",
            plan_type="demo",
            trial_start_at=datetime.utcnow(),
            trial_end_at=datetime.utcnow() + timedelta(days=7),
            subscription_active=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("✅ Usuario creado exitosamente!")
        print(f"   📧 Email: {email}")
        print(f"   🔑 Password: {password}")
        print(f"   📅 Trial hasta: {new_user.trial_end_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   🆔 User ID: {new_user.id}")
        print()
        print("🚀 Ahora puedes iniciar sesión en: https://salonplus.automatizasur.cl")
        
        return new_user
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  CREAR USUARIO DE PRUEBA - SALON PLUS")
    print("=" * 60)
    print()
    
    # Puedes cambiar estos valores
    email = input("Email del usuario (ej: prueba@test.com): ").strip()
    password = input("Contraseña (ej: test123): ").strip()
    
    if not email or not password:
        print("❌ Email y contraseña son requeridos")
        sys.exit(1)
    
    create_test_user(email, password)
