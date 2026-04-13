from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()

# Eliminar usuario si existe
existing = db.query(User).filter(User.email == 'test@test.com').first()
if existing:
    db.delete(existing)
    db.commit()

# Crear nuevo usuario
hashed_password = get_password_hash("test123")
new_user = User(email="test@test.com", hashed_password=hashed_password)
db.add(new_user)
db.commit()
print(f"Usuario creado: test@test.com / test123")
db.close()
