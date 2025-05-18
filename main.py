from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth_router, pin_router, user_router
from database import engine
import models
import schemas
from database import SessionLocal
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

FRONTEND = os.getenv("FRONTEND", "http://localhost:5173")

app = FastAPI(title="PinProject API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files for uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(pin_router, prefix="/api", tags=["pins"])
app.include_router(user_router, prefix="/api", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to PinProject API"} 