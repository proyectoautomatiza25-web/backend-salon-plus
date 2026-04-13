from datetime import timedelta
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

@router.put("/stylists/{stylist_id}", response_model=schemas.Stylist)
def update_stylist(stylist_id: str, stylist_update: schemas.StylistCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_stylist = db.query(models.Stylist).filter(models.Stylist.id == stylist_id, models.Stylist.owner_id == current_user.id).first()
    if not db_stylist:
        raise HTTPException(status_code=404, detail="Stylist not found")
    
    for key, value in stylist_update.model_dump().items():
        setattr(db_stylist, key, value)
        
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

@router.put("/services/{service_id}", response_model=schemas.Service)
def update_service(service_id: str, service_update: schemas.ServiceCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_service = db.query(models.Service).filter(models.Service.id == service_id, models.Service.owner_id == current_user.id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    for key, value in service_update.model_dump().items():
        setattr(db_service, key, value)
        
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

# --- PRODUCTS ---
@router.get("/products", response_model=List[schemas.SalonProduct])
def get_products(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    return db.query(models.SalonProduct).filter(models.SalonProduct.owner_id == current_user.id).all()

@router.post("/products", response_model=schemas.SalonProduct)
def create_product(product: schemas.SalonProductCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_product = models.SalonProduct(**product.model_dump(), owner_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=schemas.SalonProduct)
def update_product(product_id: str, product_update: schemas.SalonProductCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_product = db.query(models.SalonProduct).filter(models.SalonProduct.id == product_id, models.SalonProduct.owner_id == current_user.id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product_update.model_dump().items():
        setattr(db_product, key, value)
        
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.check_subscription_active)):
    db_product = db.query(models.SalonProduct).filter(models.SalonProduct.id == product_id, models.SalonProduct.owner_id == current_user.id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
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

# --- PUBLIC ENDPOINTS ---

@router.get("/public/{slug}", response_model=schemas.PublicSalonInfo)
def get_public_salon_info(slug: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.booking_slug == slug).first()
    if not user:
        raise HTTPException(status_code=404, detail="Salon not found")
    
    # We allow getting info even if sub is not active for the public page to show "Expired" or similar
    # But usually, it's better to show the info and then block the booking if needed.
    
    stylists = db.query(models.Stylist).filter(models.Stylist.owner_id == user.id, models.Stylist.active == True).all()
    services = db.query(models.Service).filter(models.Service.owner_id == user.id).all()
    
    return {
        "business_name": user.business_name,
        "business_logo": user.business_logo,
        "stylists": stylists,
        "services": services
    }

@router.post("/appointments/public-simple")
def public_book_simple(booking: schemas.PublicBookingCreate, db: Session = Depends(database.get_db)):
    # 1. Buscar al usuario dueño (Francis o el primer usuario admin)
    user = db.query(models.User).filter(models.User.email == "admin@agendaplus.cl").first()
    if not user:
        user = db.query(models.User).first()
        
    if not user:
        raise HTTPException(status_code=404, detail="System not configured (No owner)")

    # 2. Buscar o crear cliente (Paciente)
    client = db.query(models.SalonClient).filter(
        models.SalonClient.owner_id == user.id, 
        models.SalonClient.rut == booking.client_rut
    ).first()

    if not client and booking.client_email:
        client = db.query(models.SalonClient).filter(
            models.SalonClient.owner_id == user.id,
            models.SalonClient.email == booking.client_email
        ).first()
    
    if not client:
        client = models.SalonClient(
            owner_id=user.id,
            name=booking.client_name,
            phone=booking.client_phone,
            email=booking.client_email,
            rut=booking.client_rut,
            notes="Creado vía reserva online"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        
    # 3. Datos del servicio (Usamos un default 'Consulta General' si no viene ID)
    service = db.query(models.Service).filter(models.Service.owner_id == user.id).first()
    duration = 30
    price = 0
    service_id = None
    title = "Consulta General"

    if service:
        duration = service.duration
        price = service.price
        service_id = service.id
        title = service.name

    end_time = booking.start_time + timedelta(minutes=duration)
    
    # 4. Asegurar Profesional (Stylist)
    stylist = db.query(models.Stylist).filter(models.Stylist.owner_id == user.id).first()
    if not stylist:
        stylist = models.Stylist(
            owner_id=user.id,
            name="Dra. Francis Zabaleta",
            specialty="Medicina General",
            color="#004975"
        )
        db.add(stylist)
        db.commit()
        db.refresh(stylist)

    # 5. Crear la Cita
    db_appt = models.Appointment(
        owner_id=user.id,
        stylist_id=stylist.id,
        client_id=client.id,
        service_id=service_id,
        title=title + " (Online)",
        start_time=booking.start_time,
        end_time=end_time,
        status="confirmed",
        notes=f"Reserva Online. Motivo: {booking.notes or 'General'}",
        price=price
    )
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    
    return {"message": "Reserva Exitosa", "id": db_appt.id}
