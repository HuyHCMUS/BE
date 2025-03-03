# app/main.py
from fastapi import FastAPI
#from app.api.v1 import endpoints
from app.api.v1 import auth, vocabulary, content, messaging
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings


import os

print(settings.DATABASE_URL)
app = FastAPI(title="FastAPI PostgreSQL Template")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên specify domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
UPLOAD_FOLDER = "static/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# print(os.getcwd())

# Include routers
#app.include_router(endpoints.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(vocabulary.router, prefix=settings.API_V1_STR)
app.include_router(content.router, prefix=settings.API_V1_STR)
app.include_router(messaging.router, prefix=settings.API_V1_STR)