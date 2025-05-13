from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from auth import get_current_user

user_router = APIRouter()


@user_router.get("/users/me/pins", response_model=List[schemas.PinWithSaveStatus])
def get_user_pins(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get all pins created by the current user
    pins = db.query(models.Pin).filter(models.Pin.owner_id == current_user.id).all()
    
    # Create response data with owner information and save status
    response_data = []
    for pin in pins:
        # Check if pin is saved by current user
        saved = db.query(models.SavedPin).filter(
            models.SavedPin.pin_id == pin.id,
            models.SavedPin.user_id == current_user.id
        ).first()
        
        response_data.append({
            "id": pin.id,
            "title": pin.title,
            "description": pin.description,
            "image_url": pin.image_url,
            "created_at": pin.created_at,
            "owner_id": pin.owner_id,
            "is_saved": bool(saved),
            "owner": {
                "id": pin.owner.id,
                "email": pin.owner.email,
                "username": pin.owner.username,
                "created_at": pin.owner.created_at
            }
        })
    
    return response_data 

@user_router.get("/users/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

