# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import bcrypt
import ast
from fastapi import HTTPException
from jose import JWTError
from datetime import datetime, timedelta, timezone



from app.config import settings



def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    # print(token)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # print(payload)
        return payload
    except Exception as e:
    # Print the error message
        print(f"An error occurred: {e}")
        return None
    
def     refresh_access_token(refresh_token: str):
    try:
        decode = decode_token(refresh_token)
        data = decode['sub']
        #data_dict = ast.literal_eval(data)
        user_id = int(data)
        # print(user_id)
        new_access_token = create_token(
                data={"sub": str(user_id)},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
    
        
        return {"access_token": new_access_token}
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )