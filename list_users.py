from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()

print(f"\n{'='*60}")
print(f"USUARIOS EN LA BASE DE DATOS")
print(f"{'='*60}\n")

if not users:
    print("❌ No hay usuarios en la base de datos")
else:
    for i, user in enumerate(users, 1):
        print(f"{i}. Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Creado: {user.created_at if hasattr(user, 'created_at') else 'N/A'}")
        print()

print(f"{'='*60}")
print(f"Total de usuarios: {len(users)}")
print(f"{'='*60}\n")

db.close()
