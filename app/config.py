from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()
class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = "HS256"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL:str = os.getenv('DATABASE_URL')

settings = Settings()