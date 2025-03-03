# User model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.models.base import Base
import datetime
class vocabList(Base):
    __tablename__ = "lists"
    __table_args__ = {'schema': 'vocabulary'}
    
    list_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("auth.users.user_id"), nullable=False, index=True)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True, server_default='')
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    total_words = Column(Integer, nullable=False, server_default='0')
    progress = Column(Integer, nullable=False, server_default='0')
    image = Column(String, nullable=True, server_default='')

class vocabItem(Base):
    __tablename__ = "items"
    __table_args__ = {'schema': 'vocabulary'}
    
    item_id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("vocabulary.lists.list_id"), nullable=False, index=True)
    word = Column(String, nullable=False)
    definition = Column(String, nullable=False)
    example = Column(String, nullable=True, server_default='')
    ipa = Column(String, nullable=True, server_default='')
    audio_url_us = Column(String, nullable=True, server_default='')
    audio_url_uk = Column(String, nullable=True, server_default='')
    image_url = Column(String, nullable=True )
    difficulty_level = Column(String, nullable=True, server_default='0')
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    #updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  