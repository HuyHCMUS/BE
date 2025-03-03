from pydantic import BaseModel
from typing import List, Optional

class QuestionSchema(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    practice_type: Optional[str] = None
    question_image: Optional[str] = None
    correct_answer: str
    options: Optional[List[str]] = None
    hint: Optional[str] = None
    audio: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None

    class Config:
        from_attributes = True
