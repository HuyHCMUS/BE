from app.ai.QuestionGenerator import QuestionGenerator
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Literal, List
from sqlalchemy.orm import Session
from app.models.content import Question, QuestionContent as DBQuestionContent, Answer, QuestionMetadata as DBQuestionMetadata
import random

# Models for IELTS Speaking
class SpeakingMetadata(BaseModel):
    practice_type: Literal["speaking"] = Field("speaking", description="Type of practice, fixed as 'speaking'")
    question_type: Literal["speaking"] = Field("speaking", description="Type of question, fixed as 'speaking'")
    ielts_part: Literal["part1", "part2"] = Field(..., description="The IELTS speaking part (part1 or part2)")
    topic: str = Field(..., description="The general topic of the question")

class SpeakingQuestion(BaseModel):
    question_text: str = Field(..., description="The text of the speaking question")
    follow_up_questions: List[str] = Field(..., description="List of potential follow-up questions")

class SpeakingContent(BaseModel):
    introduction: str = Field(..., description="Brief introduction to the speaking task")   
    questions: List[SpeakingQuestion] = Field(..., description="List of main questions and their follow-ups")
    hint: str = Field(..., description="Guidance on how to answer, including tips, suggested content, structure, and strategies for handling difficult questions")
    example_answer: str = Field(..., description="A sample answer that demonstrates good speaking practices")

class IELTSSpeakingQuestion(BaseModel):
    metadata: SpeakingMetadata
    content: SpeakingContent

# Prompt templates
IELTS_SPEAKING_PROMPTS = {
    "part1": '''
IELTS Speaking Part 1: Introduction and Interview

Create an IELTS Speaking Part 1 question set on the topic: {topic}. In this part:
- The examiner asks the candidate questions about familiar topics (e.g., home, family, work, studies, interests).
- This is a 4-5 minute informal conversation designed to help candidates relax and show their ability to talk about everyday topics.

Guidelines:
- Create a main question related to the given topic.
- Add 3-5 natural follow-up questions that an examiner might ask to extend the conversation.
- Questions should be simple, direct, and conversational.
- Follow-up questions should encourage candidates to expand on their initial responses.
- Questions should not require specialized knowledge.

Return a JSON object with:
1. A brief introduction to the task
2. The main question with its follow-up questions
3. Detailed hints that include:
   - Suggested content to include in answers
   - Speaking strategies (pacing, tone, structure)
   - Tips for handling questions if the candidate is uncertain
   - Common mistakes to avoid
4. A sample answer that demonstrates good speaking practices
''',

    "part2": '''
IELTS Speaking Part 2: Individual Long Turn (Cue Card)

Create an IELTS Speaking Part 2 cue card task on the topic: {topic}. In this part:
- The candidate receives a card with a topic and specific points to address.
- They have 1 minute to prepare and should speak for 1-2 minutes without interruption.
- After the long turn, the examiner may ask 1-2 brief follow-up questions.

Guidelines:
- Create a cue card with a clear speaking task on the given topic.
- Include 3-4 specific points that the candidate should address in their response.
- The cue card should begin with "Describe..." or "Talk about..." followed by the topic.
- Add 1-2 follow-up questions that might be asked after the long turn.
- The task should be challenging but accessible to candidates of various backgrounds.

Return a JSON object with:
1. A brief introduction explaining the Part 2 task format
2. The main cue card task with its bullet points, formatted exactly as it would appear on an IELTS cue card
3. 1-2 follow-up questions
4. Detailed hints that include:
   - How to structure a 2-minute response
   - How to use the 1-minute preparation time effectively
   - Strategies for extending answers if running short on time
   - Tips for maintaining coherence and cohesion
   - Vocabulary suggestions related to the topic
5. A sample answer that demonstrates good organization and language use
'''
}

def format_question_with_followups(question_data: SpeakingQuestion) -> str:
    """Format main question with follow-up questions"""
    main_question = question_data.question_text
    follow_ups = question_data.follow_up_questions
    
    if not follow_ups:
        return main_question
    
    formatted_question = main_question + "\n\nFollow-up Questions:\n"
    for i, follow_up in enumerate(follow_ups, 1):
        formatted_question += f"{i}. {follow_up}\n"
    
    return formatted_question

def insert_speaking_question(db: Session, question_data: IELTSSpeakingQuestion):
    """Insert a speaking question directly into database using SQLAlchemy"""
    try:
        # Set default difficulty level if not provided
        difficulty_level = getattr(question_data.metadata, 'difficulty_level', 'Medium')
        
        # Process each question in the content
        for question in question_data.content.questions:
            # Format the question text to include follow-up questions
            formatted_question = format_question_with_followups(question)
            
            # Create Question instance
            db_question = Question(
                practice_type=question_data.metadata.practice_type,
                question_type=question_data.metadata.question_type,
                topic=question_data.metadata.topic,
                difficulty_level=difficulty_level
            )
            db.add(db_question)
            db.flush()  # Get the question_id without committing

            # Use introduction as context
            context = question_data.content.introduction or f"IELTS Speaking {question_data.metadata.ielts_part}"
            
            # Create QuestionContent instance
            content = DBQuestionContent(
                question_id=db_question.question_id,
                question_text=formatted_question,
                context=context
            )
            db.add(content)

            # Create Answer instance with example answer and hint
            answer = Answer(
                question_id=db_question.question_id,
                content=question_data.content.example_answer,
                is_correct=True,
                option_order=1,
                hint=question_data.content.hint,
                answer_type='text'
            )
            db.add(answer)

            # Add additional metadata
            for key, value in question_data.metadata.dict().items():
                if key not in ['practice_type', 'question_type', 'topic', 'difficulty_level']:
                    metadata = DBQuestionMetadata(
                        question_id=db_question.question_id,
                        key=key,
                        value=str(value)
                    )
                    db.add(metadata)

            db.commit()
            print(f"Successfully inserted speaking question with ID: {db_question.question_id}")
            return db_question.question_id

    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")
        raise e

def generate_speaking_question(topic: str, part: str = None, db: Session = None):
    """Generate and insert a speaking question"""
    # If part is not specified, randomly choose between part1 and part2
    if part is None:
        part = random.choice(["part1", "part2"])
    
    speaking_question = QuestionGenerator(IELTSSpeakingQuestion)
    response_dict = speaking_question.generate_question({
        "description": IELTS_SPEAKING_PROMPTS[part].format(topic=topic),
        "topic": topic
    })
    
    # Convert dict to Pydantic object
    response = IELTSSpeakingQuestion.model_validate(response_dict)
    
    if db:
        question_id = insert_speaking_question(db, response)
        return question_id
    
    return response

