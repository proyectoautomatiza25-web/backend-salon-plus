from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@agendaplus.cl').first()

if user:
    print(f"Reseteando password para: {user.email}")
    # Generar nuevo hash compatible
    new_hash = get_password_hash("admin123")
    user.hashed_password = new_hash
    db.commit()
    print("✅ Password actualizado correctamente")
else:
    print("❌ Usuario no encontrado")

db.close()
