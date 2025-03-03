from app.models.base import Base
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY

class ConversationMessages(Base):
    __tablename__ = "conversation_messages"
    __table_args__ = {'schema': 'messaging'}

    message_id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("auth.users.user_id"), nullable=False, index=True)
    content = Column(String, nullable=False)
    audio = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    feedback_score = Column(Integer, nullable=True)