from app.database import SessionLocal
from app import models, auth
from app.database import engine

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def create_admin():
    email = "admin@focus.cl"
    password = "admin"
    
    # Check if exists
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        print(f"Usuario {email} ya existe.")
        return

    hashed_pw = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    print(f"✅ Usuario creado: {email} / Password: {password}")

if __name__ == "__main__":
    create_admin()
