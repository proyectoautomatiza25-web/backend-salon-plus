from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .. import database, models, auth
import os
import requests
import hmac
import hashlib
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/billing", tags=["Billing & Subscriptions"])

FLOW_API_KEY = os.getenv("FLOW_API_KEY")
FLOW_SECRET_KEY = os.getenv("FLOW_SECRET_KEY")
FLOW_API_URL = "https://www.flow.cl/api"  # Produccion
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://salonplus.automatizasur.cl")

def get_flow_signature(params: dict) -> str:
    sorted_keys = sorted(params.keys())
    to_sign = "".join([f"{k}{params[k]}" for k in sorted_keys])
    return hmac.new(FLOW_SECRET_KEY.encode(), to_sign.encode(), hashlib.sha256).hexdigest()

def ensure_plan_exists():
    plan_id = "plan-pro-salon-plus-v2"
    params = {"apiKey": FLOW_API_KEY, "planId": plan_id}
    params["s"] = get_flow_signature(params)
    
    res = requests.get(f"{FLOW_API_URL}/plan/get", params=params)
    if res.status_code == 200:
        return plan_id
        
    create_params = {
        "apiKey": FLOW_API_KEY,
        "planId": plan_id,
        "name": "Suscripción Salon Plus Pro (Trial 7 Días)",
        "currency": "CLP",
        "amount": "39990",
        "interval": "3", # Monthly
        "trial_period_days": "7",
        "days_until_due": "3"
    }
    create_params["s"] = get_flow_signature(create_params)
    requests.post(f"{FLOW_API_URL}/plan/create", data=create_params)
    return plan_id 

@router.post("/subscribe")
async def register_card(
    request: Request,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not FLOW_API_KEY or not FLOW_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Configuración de pagos incompleta")

    try:
        # 1. Ensure Plan Exists
        plan_id = ensure_plan_exists()
        
        # 2. Create/Get Customer
        customer_params = {
            "apiKey": FLOW_API_KEY,
            "customerId": str(current_user.id),
            "name": current_user.business_name or "Usuario Salon Plus",
            "email": current_user.email
        }
        customer_params["s"] = get_flow_signature(customer_params)
        requests.post(f"{FLOW_API_URL}/customer/create", data=customer_params)

        # 3. Register Card (Get Link)
        # Use backend endpoint as return URL to handle POST -> Redirect
        base_url = str(request.base_url).replace("http://", "https://") 
        url_return = f"{base_url}api/billing/return"

        register_params = {
            "apiKey": FLOW_API_KEY,
            "customerId": str(current_user.id),
            "urlReturn": url_return
        }
        register_params["s"] = get_flow_signature(register_params)
        
        reg_res = requests.post(f"{FLOW_API_URL}/customer/register", data=register_params)
        reg_data = reg_res.json()
        
        if "url" in reg_data:
            # Append token if needed, or Flow does it? usually 'url' has query param?
            # Docs say: url + token
            full_url = reg_data["url"] + "?token=" + reg_data["token"]
            return {"checkout_url": full_url}
        else:
            print(f"Flow Register Error: {reg_res.text}")
            raise Exception(f"Error registrando tarjeta: {reg_res.text}")
            
    except Exception as e:
        print(f"Flow Error: {str(e)}")
        raise HTTPException(status_code=400, detail="No se pudo iniciar el registro de tarjeta.")

@router.post("/return", name="flow_return")
async def process_flow_return(
    token: str = Form(...), 
    db: Session = Depends(database.get_db)
):
    """
    Handle Flow POST return. Validate token, Create Subscription, Redirect to Frontend.
    """
    try:
        # 1. Check Status
        status_params = {"apiKey": FLOW_API_KEY, "token": token}
        status_params["s"] = get_flow_signature(status_params)
        
        status_res = requests.get(f"{FLOW_API_URL}/customer/registerStatus", params=status_params)
        status_data = status_res.json()
        
        # Status 1 = Registered
        if status_data.get("status") == 1:
            customer_id = status_data["customerId"] # Our User ID
            
            # Find User
            user = db.query(models.User).filter(models.User.id == customer_id).first()
            if user:
                # 2. Create Subscription
                sub_params = {
                    "apiKey": FLOW_API_KEY,
                    "planId": "plan-pro-salon-plus-v2",
                    "customerId": customer_id,
                    # "subscription_start": "" # Empty = Starts today (Trial applies)
                }
                sub_params["s"] = get_flow_signature(sub_params)
                
                sub_res = requests.post(f"{FLOW_API_URL}/subscription/create", data=sub_params)
                sub_data = sub_res.json()
                
                if "subscriptionId" in sub_data:
                    # Success!
                    user.stripe_customer_id = customer_id # Reusing field
                    user.stripe_subscription_id = sub_data["subscriptionId"]
                    user.subscription_active = True
                    user.plan_type = "pro"
                    # user.trial_end_at is handled by logic? 
                    # We can set it to now + 7 days just for UI consistency if needed
                    db.commit()
                    
                    # Redirect to Dashboard (Success)
                    return RedirectResponse(
                        url=f"{FRONTEND_URL}/?payment=success", 
                        status_code=303
                    )
                else:
                    print(f"Sub Create Error: {sub_res.text}")

        # Redirect to Dashboard (Error)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?payment=error", 
            status_code=303
        )

    except Exception as e:
        print(f"Flow Return Error: {str(e)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?payment=error", 
            status_code=303
        )
