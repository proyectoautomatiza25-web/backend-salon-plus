#!/usr/bin/env python3
"""
Script para recrear tablas con el esquema actualizado
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine
from app.models import Base
from sqlalchemy import text

def recreate_tables():
    print("🔄 Recreando tablas de la base de datos...")
    
    try:
        # Eliminar todas las tablas existentes
        print("   ⚠️  Eliminando tablas antiguas...")
        Base.metadata.drop_all(bind=engine)
        
        # Crear todas las tablas nuevas
        print("   ✨ Creando tablas nuevas...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tablas recreadas exitosamente!")
        print()
        print("Tablas creadas:")
        print("   • users (Usuarios y autenticación)")
        print("   • stylists (Profesionales/Médicos)")
        print("   • salon_clients (Pacientes)")
        print("   • appointments (Citas médicas)")
        print("   • services (Servicios)")
        print("   • salon_products (Productos)")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("  RECREAR TABLAS - AGENDA PLUS")
    print("=" * 60)
    print()
    
    if recreate_tables():
        print("🚀 Ahora puedes crear el usuario admin con:")
        print("   python create_admin_simple.py")
