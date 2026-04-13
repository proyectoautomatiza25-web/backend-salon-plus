#!/usr/bin/env python3
"""
Script para probar el login directamente
"""
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import User
from app.auth import verify_password

def test_login():
    print("=" * 60)
    print("  PRUEBA DE LOGIN - AGENDA PLUS")
    print("=" * 60)
    print()
    
    # Probar en la base de datos local
    db = SessionLocal()
    
    try:
        email = "admin@agendaplus.cl"
        password = "admin123"
        
        print(f"🔍 Buscando usuario: {email}")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ Usuario NO encontrado en la base de datos")
            return False
        
        print(f"✅ Usuario encontrado:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Business: {user.business_name}")
        print()
        
        print(f"🔐 Verificando contraseña...")
        if verify_password(password, user.hashed_password):
            print(f"✅ Contraseña CORRECTA")
        else:
            print(f"❌ Contraseña INCORRECTA")
            return False
        
        print()
        print("=" * 60)
        print("  PRUEBA DE API EN RAILWAY")
        print("=" * 60)
        print()
        
        # Probar el endpoint de login en Railway
        api_url = "https://authentic-tenderness-production-a8bc.up.railway.app/api/auth/login"
        
        print(f"📡 Probando login en: {api_url}")
        
        response = requests.post(
            api_url,
            data={
                "username": email,
                "password": password
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LOGIN EXITOSO EN RAILWAY")
            print(f"   Token: {data.get('access_token', '')[:50]}...")
            return True
        else:
            print(f"❌ ERROR EN RAILWAY:")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_login()
