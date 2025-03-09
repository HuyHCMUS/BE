# app/api/v1/content.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth import get_current_user
from sqlalchemy.exc import SQLAlchemyError
from app.ai.ConversastionQuestion import generate_conversation_question
from app.ai.SpeakingQuestion import generate_speaking_question
from app.ai.WritingQuestion import generate_writing_question
from app.ai.ReadingQuestion import generate_reading_question
import datetime

# from app.models.auth import User
from app.models.content import Question
from app.schemas.content import QuestionSchema

router = APIRouter()

@router.get("/practice/{practice_type}", response_model=dict)
async def get_practice_questions(practice_type: str,topic: str, db: Session = Depends(get_db)):
    try:
        # user = db.query(User).filter(User.user_id == current_user_id).first()
        # print(f"User:",current_user_id)
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="User not found"
        #     )
        print(topic)
        question_id = -1
        if practice_type == "conversation":
            question_id = generate_conversation_question(topic, db)
        elif practice_type == "speaking":
            question_id = generate_speaking_question(topic, db=db)
        elif practice_type == "writing":
            question_id = generate_writing_question(topic, db=db)
        elif practice_type == "reading":
            question_id = generate_reading_question(topic, db=db)

        questions = db.query(Question).filter(
            Question.practice_type == practice_type,
            (Question.parent_id == question_id) | (Question.question_id == question_id)
        ).all()
        formatted_questions = []

        for q in questions:
            content = q.content_items[0] if q.content_items else None
            options = [ans.content for ans in q.answers] if q.answers else None
            correct =[ans.is_correct for ans in q.answers]  if q.answers else None
            hint = [ans.hint for ans in q.answers] if q.answers else None
            explanation = [ans.explanation for ans in q.answers] if q.answers else None

            question_data = {
                "question_id": q.question_id,
                "question_type": q.question_type,
                "question_text": content.question_text if content else "",
                "question_context": content.context if content else "",
                "correct_answer": correct, #example: [False, True, False, False], [True], [True,False]
                "options": options, # example: [option1, option2],[short answer]
                "hint": hint,   
                "audio": content.audio_url if content and content.audio_url else None,
                "question_image": content.image_url if content and content.image_url else None,
                "explanation": explanation,
                "practice_type": q.practice_type,
                "difficulty": q.difficulty_level,
                "passage_text": content.passage_text if content else None,
                "parent_id": q.parent_id
            }
            formatted_questions.append(question_data)

        return {"status": 200, 
                "message": "Questions retrieved successfully", 
                "data": formatted_questions
                }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
