from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

# Association table for many-to-many relationship between pins and tags
pin_tags = Table(
    "pin_tags",
    Base.metadata,
    Column("pin_id", Integer, ForeignKey("pins.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    pins = relationship("Pin", back_populates="owner")
    saved_pins = relationship("SavedPin", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    pins = relationship("Pin", secondary=pin_tags, back_populates="tags")

class Pin(Base):
    __tablename__ = "pins"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="pins")
    saved_by = relationship("SavedPin", back_populates="pin", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="pin", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=pin_tags, back_populates="pins")

class SavedPin(Base):
    __tablename__ = "saved_pins"

    id = Column(Integer, primary_key=True, index=True)
    pin_id = Column(Integer, ForeignKey("pins.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    pin = relationship("Pin", back_populates="saved_by")
    user = relationship("User", back_populates="saved_pins")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    pin_id = Column(Integer, ForeignKey("pins.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    pin = relationship("Pin", back_populates="comments")
    user = relationship("User", back_populates="comments") 