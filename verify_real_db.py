#!/usr/bin/env python3
"""
Script para verificar REALMENTE qué tablas existen en la base de datos
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine
from sqlalchemy import inspect, text

def verify_database():
    print("🔍 VERIFICANDO BASE DE DATOS REAL...")
    print()
    
    try:
        # Obtener información de la conexión
        with engine.connect() as conn:
            # Verificar la URL de conexión
            print(f"📍 Conectado a: {engine.url}")
            print()
            
            # Listar todas las tablas que REALMENTE existen
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("❌ NO HAY TABLAS en la base de datos!")
                return False
            
            print(f"✅ Tablas encontradas ({len(tables)}):")
            for table in tables:
                print(f"   • {table}")
                
                # Mostrar columnas de cada tabla
                columns = inspector.get_columns(table)
                print(f"     Columnas ({len(columns)}):")
                for col in columns[:5]:  # Mostrar solo las primeras 5
                    print(f"       - {col['name']} ({col['type']})")
                if len(columns) > 5:
                    print(f"       ... y {len(columns) - 5} más")
                print()
            
            # Verificar si existe la tabla users
            if 'users' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"👥 Usuarios en la base de datos: {count}")
                
                if count > 0:
                    result = conn.execute(text("SELECT email, business_name FROM users LIMIT 5"))
                    print("   Usuarios existentes:")
                    for row in result:
                        print(f"   • {row[0]} - {row[1]}")
            
            # Verificar tabla salon_clients
            if 'salon_clients' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM salon_clients"))
                count = result.scalar()
                print(f"\n🏥 Pacientes en la base de datos: {count}")
            
            # Verificar tabla appointments
            if 'appointments' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM appointments"))
                count = result.scalar()
                print(f"📅 Citas en la base de datos: {count}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("  VERIFICACIÓN REAL DE BASE DE DATOS - AGENDA PLUS")
    print("=" * 70)
    print()
    verify_database()
