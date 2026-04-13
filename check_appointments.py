#!/usr/bin/env python3
"""
Verificar citas en la base de datos
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend-salon-plus'))

from app.database import SessionLocal
from app.models import Appointment, SalonClient, Stylist

db = SessionLocal()

print("=" * 70)
print("  VERIFICACIÓN DE CITAS EN LA BASE DE DATOS")
print("=" * 70)
print()

citas = db.query(Appointment).order_by(Appointment.start_time).all()

print(f"✅ Total citas en base de datos: {len(citas)}")
print()

if len(citas) == 0:
    print("❌ NO HAY CITAS EN LA BASE DE DATOS")
else:
    for c in citas:
        # Obtener paciente
        paciente = db.query(SalonClient).filter(SalonClient.id == c.client_id).first()
        profesional = db.query(Stylist).filter(Stylist.id == c.stylist_id).first()
        
        fecha = c.start_time.strftime("%Y-%m-%d %H:%M")
        nombre_paciente = paciente.name if paciente else "Desconocido"
        nombre_prof = profesional.name if profesional else "Desconocido"
        
        print(f"📅 {fecha}")
        print(f"   Paciente: {nombre_paciente}")
        print(f"   Profesional: {nombre_prof}")
        print(f"   Estado: {c.status}")
        print()

db.close()
