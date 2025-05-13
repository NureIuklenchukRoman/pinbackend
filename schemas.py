from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PinBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str

class PinCreate(PinBase):
    pass

class Pin(PinBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: User

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class SavedPin(BaseModel):
    id: int
    pin_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PinWithSaveStatus(Pin):
    is_saved: bool = False 