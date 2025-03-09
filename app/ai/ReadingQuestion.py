from pydantic import BaseModel, Field, validator
from typing import Literal, List, Optional, Union
import json
from app.ai.QuestionGenerator import QuestionGenerator
from sqlalchemy.orm import Session
from app.models.content import Question, QuestionContent as DBQuestionContent, Answer, QuestionMetadata as DBQuestionMetadata

# Base metadata model
class ReadingMetadata(BaseModel):
    practice_type: Literal["reading"] = Field("reading", description="Type of practice, fixed as 'reading'")
    source_type: Literal["article", "document", "story", "news", "user_provided"] = Field(..., description="Type of reading material")
    topic: str = Field(..., description="The general topic of the reading")
    difficulty_level: Literal["Beginner", "Intermediate", "Advanced"] = Field(..., description="Difficulty level of the material")

# Models for different question types

class MultipleChoiceOption(BaseModel):
    option: str = Field(..., description="The text of the answer option")
    is_correct: bool = Field(..., description="Whether this option is the correct answer")

class QuestionContent(BaseModel):
    options: Optional[List[MultipleChoiceOption]] = Field(None, description="4 options for multiple_choice and 2 options for true_false, null for short_answer")
    question_text: str = Field(..., description="The text of the question")
    sample_answer: Optional[str] = Field(None, description="A sample correct answer only for question_type is short_answer, No more than three words")
    explanation: str = Field(..., description="Explanation for correct answer")
    question_type: Literal["multiple_choice", "true_false", "short_answer"] = Field(..., description="Type of question")

    @validator('options')
    def validate_options(cls, v, values):
        question_type = values.get('question_type')
        if question_type in ['multiple_choice', 'true_false']:
            if not v:
                raise ValueError(f'options are required for {question_type} questions')
            expected_count = 4 if question_type == 'multiple_choice' else 2
            if len(v) != expected_count:
                raise ValueError(f'{question_type} questions must have exactly {expected_count} options')
            correct_count = sum(1 for opt in v if opt.is_correct)
            if correct_count != 1:
                raise ValueError('Exactly one option must be marked as correct')
        elif question_type == 'short_answer' and v:
            raise ValueError('short_answer questions should not have options')
        return v

    @validator('sample_answer')
    def validate_sample_answer(cls, v, values):
        if values.get('question_type') == 'short_answer' and not v:
            raise ValueError('sample_answer is required for short_answer questions')
        return v

# Unified Question model using Union type

# Content model
class ReadingContent(BaseModel):
    title: str = Field(..., description="Title of the reading passage")
    passage: str = Field(..., description="The full text of the reading passage")
    questions: List[QuestionContent] = Field(..., description="List of questions about the passage")

# User-provided content model (for handling existing content)
class UserProvidedContent(BaseModel):
    source_url: Optional[str] = Field(None, description="URL of the content if from web")
    document_text: Optional[str] = Field(None, description="Raw text extracted from user-provided document")
    content_type: Literal["web", "pdf", "text", "document"] = Field(..., description="Type of user-provided content")

# Main Reading Practice model
class ReadingPractice(BaseModel):
    metadata: ReadingMetadata
    content: ReadingContent
    user_provided_source: Optional[UserProvidedContent] = Field(None, description="Information about user-provided source if applicable")

# Prompt templates for generated content
READING_PROMPTS = {
    "general": '''
Reading Comprehension Practice

Create a reading comprehension practice on the topic: {topic}. The difficulty level should be {difficulty_level}.

Guidelines:
- Create an engaging and informative reading passage on the specified topic.
- The passage should be {length_guidance} (approximately {word_count} words).
- Develop {num_questions} questions that test different aspects of reading comprehension.
- Include explanations for why each answer option is correct or incorrect.
- Question type can be multile-choice (4 options), true/false (2 options), short answer (no more than three words, Sentence Completion or Short Answer Questions)
- Multiple-choice questions account for half of the total questions, with the remaining questions being true/false and short answer

Difficulty levels:
- Beginner: Simple vocabulary, clear structure, explicit information, shorter text
- Intermediate: More varied vocabulary, some inference required, more complex structure
- Advanced: Sophisticated vocabulary, requires significant inference, complex ideas 

Content types:
- Article: Informative, factual content similar to magazine or educational articles
- News: Current events or news-style reporting on a topic
- Document: Professional document format like reports, memos, or instructions
- Story: Narrative content that tells a story or presents a scenario
Content types of passage: {content_type}

Return a JSON object matching the specified schema for a ReadingPractice object.

''',

    "user_provided": '''
Reading Comprehension Question Generation

Generate reading comprehension questions for the provided content on the topic: {topic}.

Content to analyze:
```
{user_content}
```

Guidelines:
- Create {num_questions} questions that test different aspects of reading comprehension.
- Questions should be based solely on the information in the provided content.
- For multiple-choice questions, provide 4 options with only one correct answer.
- Include explanations for why each answer option is correct or incorrect.
- Identify key vocabulary from the passage and provide definitions.
- Create a brief summary of the main points.

Return a JSON object with:
1. Metadata about the reading practice (estimate difficulty based on vocabulary and structure)
2. The title and brief introduction
3. Key vocabulary with definitions and example usage
4. Questions of the specified type with correct answers and explanations
5. A summary and learning points
'''
}

# Implementation sketch of content generator (not fully implemented)
class ReadingContentGenerator:
    def __init__(self):
        self.question_generator = QuestionGenerator(ReadingPractice)
    
    def generate_from_topic(self, topic, difficulty_level="Intermediate", 
                           content_type="article", 
                           length="medium", num_questions=8):
        """Generate reading practice content from a specified topic"""
        
        length_map = {
            "short": {"guidance": "relatively short", "word_count": "200-300"},
            "medium": {"guidance": "moderate length", "word_count": "300-500"},
            "long": {"guidance": "substantial", "word_count": "500-800"}
        }
        
        length_guidance = length_map.get(length, length_map["medium"])
        
        prompt = READING_PROMPTS["general"].format(
            topic=topic,
            difficulty_level=difficulty_level,
            length_guidance=length_guidance["guidance"],
            word_count=length_guidance["word_count"],
            num_questions=num_questions,
            content_type = content_type
        )
        
        # Here we would call the LLM through QuestionGenerator
        response = self.question_generator.generate_question({
            "description": prompt,
            "topic": topic
        })
        
        return response
    
    def generate_from_user_content(self, content, content_type, topic=None, 
                                  question_type="multiple_choice", num_questions=5):
        """Generate reading practice questions from user-provided content"""
        
        if topic is None:
            # We could extract a topic from the content using LLM
            topic = "extracted topic"
        
        prompt = READING_PROMPTS["user_provided"].format(
            topic=topic,
            user_content=content[:8000],  # Limiting content length for LLM context
            num_questions=num_questions
        )
        
        # Here we would call the LLM through QuestionGenerator
        response = self.question_generator.generate_question({
            "description": prompt,
            "topic": topic
        })
        
        # Would need to combine user content with generated questions
        
        return response

# Content extraction services (implementation sketch)
# class ContentExtractor:
#     def extract_from_url(self, url):
#         """Extract content from a web URL"""
#         # Implementation would use a library like requests, BeautifulSoup, or newspaper3k
#         # to extract and clean text content from web pages
#         return {"text": "Extracted content would be here", "title": "Page Title"}
    
#     def extract_from_pdf(self, pdf_file):
#         """Extract content from a PDF file"""
#         # Implementation would use a library like PyPDF2, pdfplumber, or pdf2text
#         # to extract text content from PDF files
#         return {"text": "Extracted PDF content would be here", "title": "PDF Title"}
    
#     def extract_from_document(self, doc_file):
#         """Extract content from a document file (DOCX, etc.)"""
#         # Implementation would use a library like python-docx or textract
#         # to extract text from document files
#         return {"text": "Extracted document content would be here", "title": "Document Title"}

# Main API to use the system

def insert_reading_question(db: Session, question_data: ReadingPractice):
    """Insert a reading question directly into database using SQLAlchemy"""
    try:
        # Create main passage question
        passage_question = Question(
            practice_type=question_data.metadata.practice_type,
            question_type='passage',  # Fixed as 'passage' for main reading text
            topic=question_data.metadata.topic,
            difficulty_level=question_data.metadata.difficulty_level
        )
        db.add(passage_question)
        db.flush()  # Get the passage_question_id

        # Create passage content
        passage_content = DBQuestionContent(
            question_id=passage_question.question_id,
            question_text="Reading Passage",
            context=question_data.content.title,
            passage_text=question_data.content.passage
        )
        db.add(passage_content)

        # Add metadata for passage
        for key, value in question_data.metadata.dict().items():
            if key not in ['practice_type', 'topic', 'difficulty_level']:
                metadata = DBQuestionMetadata(
                    question_id=passage_question.question_id,
                    key=key,
                    value=str(value)
                )
                db.add(metadata)

        # Add child questions
        for question in question_data.content.questions:
            # Create child question
            child_question = Question(
                practice_type=question_data.metadata.practice_type,
                question_type=question.question_type,
                topic=question_data.metadata.topic,
                difficulty_level=question_data.metadata.difficulty_level,
                parent_id=passage_question.question_id
            )
            db.add(child_question)
            db.flush()

            # Create question content
            question_content = DBQuestionContent(
                question_id=child_question.question_id,
                question_text=question.question_text,
                context=question_data.content.title
            )
            db.add(question_content)

            # Add answers based on question type
            if question.question_type == 'short_answer':
                # For short answer questions
                answer = Answer(
                    question_id=child_question.question_id,
                    content=question.sample_answer,
                    is_correct=True,
                    option_order=1,
                    answer_type='text'
                )
                db.add(answer)
            else:
                # For multiple choice questions
                for i, option in enumerate(question.options):
                    answer = Answer(
                        question_id=child_question.question_id,
                        content=option.option,
                        is_correct=option.is_correct,
                        option_order=i + 1,
                        answer_type='option'
                    )
                    db.add(answer)

        db.commit()
        print(f"Successfully inserted reading passage and {len(question_data.content.questions)} questions")
        return passage_question.question_id

    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")
        raise e

def generate_reading_question(topic: str, difficulty_level: str = "Intermediate", 
                            content_type: str = "article", length: str = "medium", 
                            num_questions: int = 8, db: Session = None):
    """Generate and optionally insert a reading question"""
    generator = ReadingContentGenerator()
    response_dict = generator.generate_from_topic(
        topic=topic,
        difficulty_level=difficulty_level,
        content_type=content_type,
        length=length,
        num_questions=num_questions
    )
    
    # Convert dict to Pydantic object
    response = ReadingPractice.model_validate(response_dict)
    
    if db:
        question_id = insert_reading_question(db, response)
        return question_id
    
    return response
