# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.models.auth import User

from app.schemas.auth import UserCreate, UserLogin, TokenPayload
from app.services.auth import create_user, generate_tokens
from app.services.security import verify_password, refresh_access_token
from jose import JWTError

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    print(user_in)
    
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    new_user = create_user(user_in, db)

    # Create access token
    tokens = generate_tokens(new_user.user_id)
    return {
        "success": True,
        "message": "Registration successful",
        "user": {
            "id": new_user.user_id,
            "name": new_user.full_name,
            "email": new_user.email
        },
        "access_token": tokens['access_token'],
        "refresh_token": tokens['refresh_token']
    }

@router.post("/login", response_model=dict)
async def login(user_in: UserLogin, db: Session = Depends(get_db)):
    # Check if user exists
    print(user_in)
    
    user = db.query(User).filter(User.email == user_in.email).first()
    print(user.user_id, user.full_name, user.email)
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
        )
    else:
        print("Login successful")
    # Create access token
    tokens = generate_tokens(user.user_id)
    return {
        "success": True,
        "message": "Registration successful",
        "user": {
            "id": user.user_id,
            "name": user.full_name,
            "email": user.email
        },
        "access_token": tokens['access_token'],
        "refresh_token": tokens['refresh_token']
    }

@router.post("/refresh", response_model=dict)
async def refresh_token(token_payload: TokenPayload):
    try:
        token = refresh_access_token(token_payload.refresh_token)
        print(token,'OK')    
        return {
                "access_token": token["access_token"],
                "token_type": "bearer"
            }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )