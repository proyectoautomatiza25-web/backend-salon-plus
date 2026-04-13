from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Registro del usuario exitoso, no generamos link de Mercado Pago
    new_user.checkout_url = None

    # Send Welcome Email
    try:
        from ..services import email_service
        email_service.send_welcome_email(new_user.email)
    except Exception as e:
        print(f"Error sending email: {e}")
        
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.User)
def update_me(user_update: schemas.UserUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if user_update.booking_slug:
        # Check if slug is taken by someone else
        existing = db.query(models.User).filter(models.User.booking_slug == user_update.booking_slug).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="El link de reserva ya está ocupado por otro salón.")
            
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/forgot-password")
def forgot_password(request: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Buscamos al usuario por email
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        # Por seguridad no decimos si existe o no, pero devolvemos éxito fingido
        return {"message": "Si el correo está registrado, recibirá instrucciones a la brevedad."}
    
    # Aquí iría el envío de email real con el token de recuperación
    try:
        from ..services import email_service
        # email_service.send_reset_password_email(user.email)
        print(f"DEBUG: Enviando recuperación a {user.email}")
    except Exception as e:
        print(f"Error en recuperación: {e}")

    return {"message": "Si el correo está registrado, recibirá instrucciones a la brevedad."}
