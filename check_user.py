from app.database import SessionLocal
from app.models import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@agendaplus.cl').first()
if user:
    print(f"Usuario encontrado: {user.email}")
    print(f"ID: {user.id}")
else:
    print("Usuario NO existe")
db.close()
