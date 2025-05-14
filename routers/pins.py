from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import logging
from database import get_db
import models
import schemas
from auth import get_current_user
from schemas import Comment, CommentCreate, Tag, TagCreate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pin_router = APIRouter()

@pin_router.post("/pins/", response_model=schemas.Pin)
async def create_pin(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...),
    tags: Optional[str] = Form(None),  # Comma-separated list of tags
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"Creating pin with title: {title}")
        logger.info(f"Description: {description}")
        logger.info(f"Image filename: {image.filename}")
        
        # Create static directory if it doesn't exist
        os.makedirs("static/uploads", exist_ok=True)
        
        # Save the uploaded image
        file_location = f"static/uploads/{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        
        # Create the pin
        db_pin = models.Pin(
            title=title,
            description=description,
            image_url=f"/static/uploads/{image.filename}",
            owner_id=current_user.id
        )
        db.add(db_pin)
        db.flush()  # Flush to get the pin ID
        
        # Process tags if provided
        if tags:
            tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]
            for tag_name in tag_names:
                # Get or create tag
                db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
                if not db_tag:
                    db_tag = models.Tag(name=tag_name)
                    db.add(db_tag)
                    db.flush()
                db_pin.tags.append(db_tag)
        
        db.commit()
        db.refresh(db_pin)
        logger.info(f"Successfully created pin with ID: {db_pin.id}")
        return db_pin
    except Exception as e:
        logger.error(f"Error creating pin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@pin_router.get("/pins/", response_model=List[schemas.Pin])
def get_pins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    pins = db.query(models.Pin).offset(skip).limit(limit).all()
    return pins

@pin_router.get("/pins/saved", response_model=List[schemas.PinWithSaveStatus])
def get_saved_pins(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Print current user in red
    print(f"\033[91mCurrent User: {current_user}\033[0m")
    
    # Get all pins that are saved by the current user
    saved_pins = db.query(models.Pin).join(
        models.SavedPin,
        models.Pin.id == models.SavedPin.pin_id
    ).filter(
        models.SavedPin.user_id == current_user.id
    ).all()
    
    # Create response data with owner information and save status
    response_data = []
    for pin in saved_pins:
        response_data.append({
            "id": pin.id,
            "title": pin.title,
            "description": pin.description,
            "image_url": pin.image_url,
            "created_at": pin.created_at,
            "owner_id": pin.owner_id,
            "is_saved": True,  # All pins in this list are saved
            "owner": {
                "id": pin.owner.id,
                "email": pin.owner.email,
                "username": pin.owner.username,
                "created_at": pin.owner.created_at
            }
        })
    
    return response_data

@pin_router.get("/pins/{pin_id}", response_model=schemas.PinWithSaveStatus)
def get_pin(
    pin_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    pin = db.query(models.Pin).join(models.User).filter(models.Pin.id == pin_id).first()
    if pin is None:
        raise HTTPException(status_code=404, detail="Pin not found")
    
    # Check if pin is saved by current user
    is_saved = False
    if current_user:
        saved = db.query(models.SavedPin).filter(
            models.SavedPin.pin_id == pin_id,
            models.SavedPin.user_id == current_user.id
        ).first()
        is_saved = bool(saved)
    
    # Create response data with owner information
    response_data = {
        "id": pin.id,
        "title": pin.title,
        "description": pin.description,
        "image_url": pin.image_url,
        "created_at": pin.created_at,
        "owner_id": pin.owner_id,
        "is_saved": is_saved,
        "owner": {
            "id": pin.owner.id,
            "email": pin.owner.email,
            "username": pin.owner.username,
            "created_at": pin.owner.created_at
        }
    }
    
    return response_data

@pin_router.post("/pins/{pin_id}/save", response_model=schemas.SavedPin)
def save_pin(
    pin_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if pin exists
    pin = db.query(models.Pin).filter(models.Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    
    # Check if already saved
    existing_save = db.query(models.SavedPin).filter(
        models.SavedPin.pin_id == pin_id,
        models.SavedPin.user_id == current_user.id
    ).first()
    
    if existing_save:
        raise HTTPException(status_code=400, detail="Pin already saved")
    
    # Create new save
    saved_pin = models.SavedPin(
        pin_id=pin_id,
        user_id=current_user.id
    )
    db.add(saved_pin)
    db.commit()
    db.refresh(saved_pin)
    return saved_pin

@pin_router.delete("/pins/{pin_id}/save")
def unsave_pin(
    pin_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    saved_pin = db.query(models.SavedPin).filter(
        models.SavedPin.pin_id == pin_id,
        models.SavedPin.user_id == current_user.id
    ).first()
    
    if not saved_pin:
        raise HTTPException(status_code=404, detail="Pin not saved")
    
    db.delete(saved_pin)
    db.commit()
    return {"message": "Pin unsaved successfully"}

@pin_router.delete("/pins/{pin_id}")
def delete_pin(
    pin_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    pin = db.query(models.Pin).filter(models.Pin.id == pin_id).first()
    if pin is None:
        raise HTTPException(status_code=404, detail="Pin not found")
    if pin.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this pin")
    
    # Delete the image file
    if pin.image_url:
        try:
            os.remove(f"static/{pin.image_url.split('/static/')[-1]}")
        except:
            pass
    
    db.delete(pin)
    db.commit()
    return {"message": "Pin deleted successfully"}

@pin_router.get("/pins/{pin_id}/comments", response_model=List[Comment])
def get_comments_for_pin(
    pin_id: int,
    db: Session = Depends(get_db)
):
    comments = db.query(models.Comment).filter(models.Comment.pin_id == pin_id).order_by(models.Comment.created_at.asc()).all()
    return comments

@pin_router.post("/pins/{pin_id}/comments", response_model=Comment)
def create_comment_for_pin(
    pin_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_comment = models.Comment(
        content=comment.content,
        pin_id=pin_id,
        user_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@pin_router.get("/tags/", response_model=List[Tag])
def get_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    tags = db.query(models.Tag).offset(skip).limit(limit).all()
    return tags

@pin_router.get("/pins/tag/{tag_name}", response_model=List[schemas.Pin])
def get_pins_by_tag(
    tag_name: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    pins = db.query(models.Pin).join(
        models.pin_tags
    ).join(
        models.Tag
    ).filter(
        models.Tag.id == tag.id
    ).offset(skip).limit(limit).all()
    
    return pins 