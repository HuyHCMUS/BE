from pydantic import BaseModel

from pydantic import BaseModel
from typing import Optional


class VocabListSchema(BaseModel):
    list_id: Optional[int] = None
    title: str
    category: str
    description: Optional[str] = None
    total_words: Optional[int] = 0
    progress: Optional[int] = 0
    image: Optional[str] = None
    image_base64:  Optional[str] = None 

    class Config:
        from_attributes = True

class vocabItemSchema(BaseModel):
    item_id: Optional[int] = None
    list_id: int
    word: str
    definition: str
    example: Optional[str] = None
    ipa: Optional[str] = None
    image_url: Optional[str] = None
    image_base64:  Optional[str] = None
    difficult_level: Optional[str] = '0'

    class Config:
        from_attributes = True
