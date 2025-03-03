# app/api/v1/vocabulary.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth import get_current_user
from sqlalchemy.exc import SQLAlchemyError
from app.ai.Chatbot import Chatbot
from app.ai.ErrorDetection import ErrorDetection

from app.models.messaging import ConversationMessages
from app.schemas.messaging import ConversationMessageSchema, SuggestionRequest

router = APIRouter()
chatbot = Chatbot()
errorDetection = ErrorDetection()
@router.post("/messages", response_model=dict)
async def response_message(message: ConversationMessageSchema, 
                           db: Session = Depends(get_db), 
                           current_user_id = Depends(get_current_user)):
    try:

        responses = chatbot.generate_response(message.content,db,current_user_id)
        error = errorDetection.analyze_sentence(sentence=message.content)
        print(error)
        responses.update({'error':error})

        user_message = ConversationMessages(sender="user", user_id=current_user_id, content=message.content)
        db.add(user_message)
        for bot_message in responses['messages']:
            bot_message = ConversationMessages(sender="bot", user_id=current_user_id, content=bot_message)
            db.add(bot_message)

        
        
        
        db.commit()
        return {"status": 200, 
                "message": "Message sent successfully", 
                "data": responses,
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
    
@router.post("/suggestions", response_model=dict)
async def response_suggestions(request: SuggestionRequest,
                               db: Session = Depends(get_db), 
                               current_user_id = Depends(get_current_user)):
    try:
        suggestions = [
            f"Suggestion 1 for {request.content}",
            f"Suggestion 2 for {request.content}",
            f"Suggestion 3 for {request.content}"
        ]
        return {
            "status": 200, 
            "message": "Suggestions retrieved successfully", 
            "data": suggestions
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
