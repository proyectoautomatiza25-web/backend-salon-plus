"""
Script para crear un usuario de prueba para el Dashboard.
"""
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()

try:
    # Verificar si ya existe
    existing = db.query(User).filter(User.email == "demo@focus.com").first()
    if existing:
        print("✅ Usuario demo ya existe")
        print(f"   Email: demo@focus.com")
        print(f"   Password: demo123")
    else:
        # Crear usuario demo
        demo_user = User(
            email="demo@focus.com",
            hashed_password=get_password_hash("demo123"),
            business_name="Restaurante Demo",
            subscription_active=True,
            plan_type="pro"
        )
        db.add(demo_user)
        db.commit()
        print("✅ Usuario demo creado exitosamente")
        print(f"   Email: demo@focus.com")
        print(f"   Password: demo123")
        
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
