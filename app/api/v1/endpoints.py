# app/api/v1/endpoints.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
router = APIRouter()

@router.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Hello World", "database": "Connected"}

@router.get("/test")
def ditmemay(db: Session = Depends(get_db)):
    test = db.query(User).offset(0).limit(1).one()
    return {"user": test}