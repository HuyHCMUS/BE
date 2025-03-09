from app.ai.QuestionGenerator import QuestionGenerator
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy.orm import Session
from app.models.content import Question, QuestionContent as DBQuestionContent, Answer, QuestionMetadata as DBQuestionMetadata

class QuestionContent(BaseModel):
    question_text: str = Field(..., description="The text of the question with a blank to fill in")
    correct_answer: str = Field(..., description="The correct answer to fill in the blank")
    hint: str = Field(..., description="A hint to help the user answer the question")

class QuestionMetadata(BaseModel):
    practice_type: Literal["conversation"] = Field("conversation", description="Type of practice, fixed as 'conversation'")
    question_type: Literal["fill_in"] = Field("fill_in", description="Type of question, fixed as 'fill_in'")
    topic: str = Field(..., description="The general topic of the question, provided by the user")
    conversation_context: str = Field(..., description="The specific context of the conversation, e.g., 'Asking for Directions'")
    difficulty_level: Literal["Easy", "Medium", "Hard"] = Field("Easy", description="Difficulty level of the question")


class ConversationQuestion(BaseModel):
    metadata: QuestionMetadata
    content: QuestionContent

conversation_description = '''This exercise helps learners improve their English conversation skills. Provide a two-person dialogue with a missing response. The learner must complete the response naturally, ensuring it fits the context.   

- It should contain between 1 to 4 exchanges (turns) between the two speakers. 
- The conversation should be practical and realistic.  
- The missing response should be a full sentence, not just a single word.  
- The missing response can be the opening or a reply within the conversation.  
- Provide a correct answer that sounds natural and relevant.  
- Include a hint to guide the learner without giving the exact answer. 
- The conversation can be about any subject related to the given topic. 
- Adjust the difficulty level based on the following:  
  - **Easy:**
  - **Medium:** 
  - **Hard:** 
'''


def insert_conversation_question(db: Session, question_data: ConversationQuestion):
    """Insert a conversation question directly into database using SQLAlchemy"""
    try:
        # Create Question instance
        question = Question(
            practice_type=question_data.metadata.practice_type,
            question_type=question_data.metadata.question_type,
            topic=question_data.metadata.topic,
            difficulty_level=question_data.metadata.difficulty_level
        )
        db.add(question)
        db.flush()  # Get the question_id without committing

        # Create QuestionContent instance
        content = DBQuestionContent(
            question_id=question.question_id,
            question_text=question_data.content.question_text,
            context=question_data.metadata.conversation_context
        )
        db.add(content)

        # Create Answer instance
        answer = Answer(
            question_id=question.question_id,
            content=question_data.content.correct_answer,
            is_correct=True,
            option_order=1,
            hint=question_data.content.hint,
            answer_type='text'
        )
        db.add(answer)

        # Add additional metadata
        for key, value in question_data.metadata.dict().items():
            if key not in ['practice_type', 'question_type', 'topic', 'difficulty_level', 'conversation_context']:
                metadata = DBQuestionMetadata(
                    question_id=question.question_id,
                    key=key,
                    value=str(value)
                )
                db.add(metadata)

        db.commit()
        print(f"Successfully inserted conversation question with ID: {question.question_id}")
        return question.question_id

    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")
        raise e

def generate_conversation_question(topic, db: Session):
    conversation_question = QuestionGenerator(ConversationQuestion)
    response_dict = conversation_question.generate_question({
        "description": conversation_description,
        "topic": topic
    })
    # Convert dict to Pydantic object
    response = ConversationQuestion.model_validate(response_dict)  # For Pydantic v2
    # OR use this for Pydantic v1
    # response = ConversationQuestion.parse_obj(response_dict)
    
    question_id = insert_conversation_question(db, response)
    return question_id
    

