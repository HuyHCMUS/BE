from app.ai.QuestionGenerator import QuestionGenerator
from langchain_core.output_parsers import JsonOutputParser

from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from sqlalchemy.orm import Session
from app.models.content import Question, QuestionContent as DBQuestionContent, Answer, QuestionMetadata as DBQuestionMetadata
import json
import random

class WritingMetadata(BaseModel):
    practice_type: Literal["writing"] = Field("writing", description="Type of practice, fixed as 'writing'")
    ielts_type: Literal["academic", "general"] = Field(..., description="The IELTS exam type: academic or general")
    task_number: Literal["task1", "task2"] = Field(..., description="The IELTS writing task number (task1 or task2)")
    topic: str = Field(..., description="The general topic of the writing task")

class WritingContent(BaseModel):
    task_description: str = Field(..., description="The full description of the writing task")
    data_source: Optional[str] = Field(None, description="Visual data description for Academic Task 1 (chart, graph, etc.)")
    hints: List[str] = Field(..., description="List of helpful hints for completing the task effectively")
    structure_guide: str = Field(..., description="Guidance on how to structure the response")
    vocabulary_suggestions: List[str] = Field(..., description="Key vocabulary or phrases that could be useful")

class IELTSWritingQuestion(BaseModel):
    metadata: WritingMetadata
    content: WritingContent

# Prompt templates
IELTS_WRITING_PROMPTS = {
    "academic_task1": '''
IELTS Academic Writing Task 1

Create an IELTS Academic Writing Task 1 question on the topic: {topic}

In this task:
- Test-takers are presented with a graph, table, chart, or diagram and asked to describe, summarize, or explain the information in their own words.
- They must write at least 150 words in about 20 minutes.
- They should not give opinions but focus on objective description and highlighting significant features.

Guidelines:
- Create a clear, realistic prompt with a visual data source (graph, chart, table, or diagram).
- Include a detailed description of what the visual data shows (since we can't include actual visuals).
- Provide helpful hints that guide the test-taker on how to approach the task.
- Include structure guidance, vocabulary suggestions.

Return a JSON object with:
1. Task description (the actual prompt)
2. A detailed description of the visual data source
3. A list of helpful hints for approaching the task
4. Structure guidance for organizing the response
5. Key vocabulary suggestions relevant to the task
''',

    "task2": '''
IELTS Writing Task 2 (Academic & General Training)

Create an IELTS Writing Task 2 question on the topic: {topic}

In this task:
- Test-takers are presented with a point of view, argument, or problem and asked to write an essay in response.
- They must write at least 250 words in about 40 minutes.
- They should present a position or argument with supporting evidence.

Guidelines:
- Create a clear, thought-provoking prompt that requires analysis and argumentation.
- For Academic: Make the prompt slightly more formal and abstract, potentially requiring more complex analysis.
- For General: Make the prompt relate more to everyday experiences and practical situations.
- The prompt should be appropriate for an international audience and not culturally biased.
- The task should be complex enough to allow for nuanced discussion but clear enough to respond to in 40 minutes.
- Provide helpful hints that guide the test-taker on how to approach different aspects of the argument.
- Include structure guidance, vocabulary suggestions.
- Remember to indicate whether this is for Academic or General Training in the metadata.

Return a JSON object with:
1. Task description (the actual prompt)
2. Word count and time allocation recommendations
3. A list of helpful hints for approaching the task
4. Structure guidance for organizing the essay
5. Key vocabulary suggestions relevant to the topic
6. Common mistakes to avoid
''',

    "general_task1": '''
IELTS General Training Writing Task 1

Create an IELTS General Training Writing Task 1 question on the topic: {topic}

In this task:
- Test-takers are asked to write a letter requesting information or explaining a situation.
- They must write at least 150 words in about 20 minutes.
- The letter can be formal, semi-formal, or informal depending on the context.

Guidelines:
- Create a realistic scenario requiring a letter (request, complaint, explanation, etc.).
- Clearly specify the recipient, purpose, and at least 3 content points to address.
- Indicate whether a formal, semi-formal, or informal letter is required.
- Provide helpful hints that guide the test-taker on how to approach the task.
- Include structure guidance, vocabulary suggestions for the appropriate register

Return a JSON object with:
1. Task description (the actual prompt)
2. A list of helpful hints for approaching the task
3. Structure guidance for organizing the letter
4. Key vocabulary suggestions relevant to the letter type and topic
''',

    
}

def generate_ielts_writing_question(topic, ielts_type=None, task_number=None):
    """
    Generate an IELTS writing question based on the given parameters.
    If ielts_type or task_number is not specified, randomly select one.
    """
    # Determine IELTS type if not specified
    if not ielts_type:
        ielts_type = random.choice(["academic", "general"])
    
    # Determine task number if not specified
    if not task_number:
        task_number = random.choice(["task1", "task2"])
    
    # Create the prompt key
    prompt_key = f"{ielts_type}_{task_number}"
    prompt_key = "academic_task1"
    
    # Format the prompt with the topic
    prompt = IELTS_WRITING_PROMPTS[prompt_key].format(topic=topic)
    
    # Generate the question
    question_generator = QuestionGenerator(IELTSWritingQuestion)
    response = question_generator.generate_question({
        "description": prompt,
        "topic": topic
    })
    
    return response

def format_hints_and_vocabulary(hints: List[str], vocabulary: List[str]) -> str:
    """Format hints and vocabulary into a single string"""
    formatted_hint = ""
    
    # Add the hints section
    if hints:
        for i, hint in enumerate(hints, 1):
            formatted_hint += f"{i}. {hint}\n"
        formatted_hint += "\n"
    
    # Add vocabulary suggestions
    if vocabulary:
        formatted_hint += "VOCABULARY SUGGESTIONS:\n"
        formatted_hint += ", ".join(vocabulary)
    
    return formatted_hint

def insert_writing_question(db: Session, question_data: IELTSWritingQuestion):
    """Insert a writing question directly into database using SQLAlchemy"""
    try:
        # Create Question instance
        db_question = Question(
            practice_type=question_data.metadata.practice_type,
            question_type='writing',  # Fixed as 'writing'
            topic=question_data.metadata.topic,
            difficulty_level='Medium'  # Default difficulty
        )
        db.add(db_question)
        db.flush()

        # Create QuestionContent instance
        context = f"IELTS {question_data.metadata.ielts_type} - {question_data.metadata.task_number}"
        content = DBQuestionContent(
            question_id=db_question.question_id,
            question_text=question_data.content.task_description,
            context=context,
            passage_text=question_data.content.data_source if question_data.content.data_source else None
        )
        db.add(content)

        # Format hints and vocabulary
        combined_hint = format_hints_and_vocabulary(
            question_data.content.hints,
            question_data.content.vocabulary_suggestions
        )

        # Create Answer instance
        answer = Answer(
            question_id=db_question.question_id,
            content=question_data.content.structure_guide,  # Structure guide as the "answer"
            is_correct=True,
            option_order=1,
            hint=combined_hint,
            answer_type='text'
        )
        db.add(answer)

        # Add additional metadata
        for key, value in question_data.metadata.dict().items():
            if key not in ['practice_type', 'topic', 'difficulty_level']:
                metadata = DBQuestionMetadata(
                    question_id=db_question.question_id,
                    key=key,
                    value=str(value)
                )
                db.add(metadata)

        db.commit()
        print(f"Successfully inserted writing question with ID: {db_question.question_id}")
        return db_question.question_id

    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")
        raise e

def generate_writing_question(topic: str, ielts_type: str = None, task_number: str = None, db: Session = None):
    """Generate and optionally insert a writing question"""
    response_dict = generate_ielts_writing_question(topic, ielts_type, task_number)
    
    # Convert dict to Pydantic object
    response = IELTSWritingQuestion.model_validate(response_dict)
    
    if db:
        question_id = insert_writing_question(db, response)
        return question_id
    
    return response

