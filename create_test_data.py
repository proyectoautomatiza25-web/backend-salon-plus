#!/usr/bin/env python3
"""
Script para crear datos de prueba: profesionales y pacientes
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import User, Stylist, SalonClient

def create_test_data():
    print("=" * 60)
    print("  CREAR DATOS DE PRUEBA - AGENDA PLUS")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Obtener el usuario admin
        user = db.query(User).filter(User.email == "admin@agendaplus.cl").first()
        
        if not user:
            print("❌ Usuario admin no encontrado")
            return False
        
        print(f"✅ Usuario encontrado: {user.email}")
        print()
        
        # Crear profesionales
        print("👨‍⚕️ Creando profesionales...")
        
        professionals = [
            {
                "name": "Dr. Juan Pérez",
                "specialty": "Medicina General",
                "color": "#3b82f6"
            },
            {
                "name": "Dra. María González",
                "specialty": "Pediatría",
                "color": "#10b981"
            },
            {
                "name": "Dr. Carlos Rodríguez",
                "specialty": "Cardiología",
                "color": "#f59e0b"
            }
        ]
        
        created_profs = []
        for prof_data in professionals:
            # Verificar si ya existe
            existing = db.query(Stylist).filter(
                Stylist.owner_id == user.id,
                Stylist.name == prof_data["name"]
            ).first()
            
            if existing:
                print(f"   ⚠️  {prof_data['name']} ya existe")
                created_profs.append(existing)
            else:
                prof = Stylist(
                    owner_id=user.id,
                    name=prof_data["name"],
                    specialty=prof_data["specialty"],
                    color=prof_data["color"],
                    active=True
                )
                db.add(prof)
                db.flush()
                created_profs.append(prof)
                print(f"   ✅ {prof_data['name']} creado")
        
        db.commit()
        print()
        
        # Crear pacientes de prueba
        print("👥 Creando pacientes de prueba...")
        
        patients = [
            {
                "name": "Ana Martínez",
                "rut": "12345678-9",
                "phone": "+56912345678",
                "email": "ana@email.com",
                "prevision": "Fonasa",
                "category": "General"
            },
            {
                "name": "Pedro Silva",
                "rut": "98765432-1",
                "phone": "+56987654321",
                "email": "pedro@email.com",
                "prevision": "Isapre Colmena",
                "category": "Crónico"
            }
        ]
        
        for patient_data in patients:
            # Verificar si ya existe
            existing = db.query(SalonClient).filter(
                SalonClient.owner_id == user.id,
                SalonClient.rut == patient_data["rut"]
            ).first()
            
            if existing:
                print(f"   ⚠️  {patient_data['name']} ya existe")
            else:
                patient = SalonClient(
                    owner_id=user.id,
                    **patient_data
                )
                db.add(patient)
                print(f"   ✅ {patient_data['name']} creado")
        
        db.commit()
        print()
        
        print("🎉 Datos de prueba creados exitosamente!")
        print()
        print(f"📊 Resumen:")
        print(f"   • {len(created_profs)} profesionales")
        print(f"   • {len(patients)} pacientes")
        print()
        print("🚀 Recarga la aplicación para ver los datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
