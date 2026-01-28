from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, schemas, auth

router = APIRouter(prefix="/api/salon", tags=["Salon SaaS"])

# --- DEPENDENCY ---
# We use auth.get_current_user to ensure only authenticated users access these routes

# --- STYLISTS ---
@router.get("/stylists", response_model=List[schemas.Stylist])
def get_stylists(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    return db.query(models.Stylist).filter(models.Stylist.owner_id == current_user.id).all()

@router.post("/stylists", response_model=schemas.Stylist)
def create_stylist(stylist: schemas.StylistCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_stylist = models.Stylist(**stylist.model_dump(), owner_id=current_user.id)
    db.add(db_stylist)
    db.commit()
    db.refresh(db_stylist)
    return db_stylist

@router.delete("/stylists/{stylist_id}")
def delete_stylist(stylist_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_stylist = db.query(models.Stylist).filter(models.Stylist.id == stylist_id, models.Stylist.owner_id == current_user.id).first()
    if not db_stylist:
        raise HTTPException(status_code=404, detail="Stylist not found")
    db.delete(db_stylist)
    db.commit()
    return {"message": "Deleted"}

# --- SERVICES ---
@router.get("/services", response_model=List[schemas.Service])
def get_services(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    return db.query(models.Service).filter(models.Service.owner_id == current_user.id).all()

@router.post("/services", response_model=schemas.Service)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_service = models.Service(**service.model_dump(), owner_id=current_user.id)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/services/{service_id}")
def delete_service(service_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_service = db.query(models.Service).filter(models.Service.id == service_id, models.Service.owner_id == current_user.id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(db_service)
    db.commit()
    return {"message": "Deleted"}

# --- CLIENTS ---
@router.get("/clients", response_model=List[schemas.SalonClient])
def get_clients(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    return db.query(models.SalonClient).filter(models.SalonClient.owner_id == current_user.id).all()

@router.post("/clients", response_model=schemas.SalonClient)
def create_client(client: schemas.SalonClientCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_client = models.SalonClient(**client.model_dump(), owner_id=current_user.id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.put("/clients/{client_id}", response_model=schemas.SalonClient)
def update_client(client_id: str, client_update: schemas.SalonClientCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_client = db.query(models.SalonClient).filter(models.SalonClient.id == client_id, models.SalonClient.owner_id == current_user.id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    for key, value in client_update.model_dump().items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/clients/{client_id}")
def delete_client(client_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_client = db.query(models.SalonClient).filter(models.SalonClient.id == client_id, models.SalonClient.owner_id == current_user.id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(db_client)
    db.commit()
    return {"message": "Deleted"}

# --- APPOINTMENTS ---
@router.get("/appointments", response_model=List[schemas.Appointment])
def get_appointments(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    return db.query(models.Appointment).filter(models.Appointment.owner_id == current_user.id).all()

@router.post("/appointments", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    # Verify dependencies exist?
    # For now, just create
    db_appt = models.Appointment(**appointment.model_dump(), owner_id=current_user.id)
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return db_appt

@router.put("/appointments/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(appointment_id: str, appt_update: schemas.AppointmentCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id, models.Appointment.owner_id == current_user.id).first()
    if not db_appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    for key, value in appt_update.model_dump().items():
        setattr(db_appt, key, value)
        
    db.commit()
    db.refresh(db_appt)
    return db_appt

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id, models.Appointment.owner_id == current_user.id).first()
    if not db_appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(db_appt)
    db.commit()
    return {"message": "Deleted"}
