
from app.models.auth import User
from app.schemas.auth import UserCreate
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services.security import get_password_hash, create_token, decode_token
from datetime import timedelta
from app.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError
import ast




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_user(user_create: UserCreate, db: Session):
    # Hash mật khẩu
    hashed_password = get_password_hash(user_create.password)
    
    # Tạo đối tượng người dùng mới
    new_user = User(
        full_name=user_create.name,
        email=user_create.email,
        password_hash=hashed_password
    )
    
    # Lưu vào database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# Create access token
def get_access_token(user_id):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
            data={"sub": str(user_id)}, 
            expires_delta=access_token_expires
        )   
    #print(access_token)
    return access_token

def generate_tokens(user_id):
    # Tạo access token (ngắn hạn)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": str(user_id)}, 
        expires_delta=access_token_expires
    )
    
    # Tạo refresh token (dài hạn)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_token(
        data={"sub": str(user_id)},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã token
        #print(token)
        decode = decode_token(token)
        data = decode['sub'] 
        # print(type(data))
        # data_dict = ast.literal_eval(data)
        user_id = int(data)
        # user_id = data_dict['user_id']
    except:
        raise credentials_exception
    print('Đã xác thực user')
    #user = db.query(User).filter(User.user_id == user_id).first()
    return user_id
