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

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PinBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str
    tags: Optional[List[str]] = []

class PinCreate(PinBase):
    pass

class Pin(PinBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: User
    tags: List[Tag] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    created_at: datetime
    user: User
    pin_id: int

    class Config:
        from_attributes = True

class SavedPin(BaseModel):
    id: int
    pin_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PinWithSaveStatus(Pin):
    is_saved: bool = False 