
from pydantic import BaseModel
from typing import Optional

class ConversationMessageSchema(BaseModel):

    content: str
    sender: str
    audio: Optional[str] = None

    class Config:
        from_attributes = True

class SuggestionRequest(BaseModel):
    content: str
