from QuestionGenerator import QuestionGenerator
from langchain_core.output_parsers import  JsonOutputParser

from pydantic import BaseModel, Field
from typing import Literal,List
import json

class AnswerOption(BaseModel):
    option: str = Field(..., description="The text of the answer option")
    is_correct: bool = Field(..., description="Whether this option is the correct answer")

class Question(BaseModel):
    question_text: str = Field(..., description="The text of the question about the audio")
    options: List[AnswerOption] = Field(..., description="The multiple-choice options for this question")

class ListeningMetadata(BaseModel):
    practice_type: Literal["listening"] = Field("listening", description="Type of practice, fixed as 'listening'")
    question_type: Literal["multiple_choice"] = Field("multiple_choice", description="Type of question, fixed as 'multiple_choice'")
    toeic_part: Literal["part2", "part3", "part4"] = Field(..., description="The TOEIC listening part (part2, part3, or part4)")
    topic: str = Field(..., description="The general topic of the question")
    difficulty_level: Literal["Easy", "Medium", "Hard"] = Field(..., description="Difficulty level of the question")

# Unified Content structure for all TOEIC listening parts
class ListeningContent(BaseModel):
    context: str = Field("", description="Brief description of the audio context (optional for Part 2)")
    audio_transcript: str = Field(..., description="The full transcript of what would be heard in the audio")
    questions: List[Question] = Field(..., description="List of questions about the audio, each with multiple choices")
    hint: str = Field(..., description="A general hint to help the learner")

# Unified model for all TOEIC listening parts
class TOEICListeningQuestion(BaseModel):
    metadata: ListeningMetadata
    content: ListeningContent

# Prompt templates
TOEIC_PROMPTS = {
    "part2": '''
TOEIC Listening Part 2: Question-Response

Create a question-response item similar to TOEIC Part 2. In this part:
- The audio contains a single question or statement.
- The test-taker must choose the most appropriate response from three options.
- Only the question is spoken; the options are written.

Guidelines:
- Create a clear, natural-sounding question or statement in English on the topic given by user.
- For Part 2, the "question" is the audio transcript.
- Create a single question with three possible responses (A, B, C), only one of which correctly answers the audio question.
- Incorrect options should be plausible but clearly wrong when carefully analyzed.
- Questions should reflect real-life situations in professional or daily life contexts.
- Audio transcript should be 1-2 sentences (10-15 words maximum).

Difficulty levels:
- Easy: Simple vocabulary, clear question intent, straightforward correct answer
- Medium: More varied vocabulary, may require inference, answer not immediately obvious
- Hard: Complex vocabulary or structure, subtle differences between options, requires careful listening comprehension


Return a JSON object with:
1. A brief context (leave empty for Part 2 or very minimal)
2. The audio transcript (the spoken question)
3. One question with three response options (A, B, C), marking which one is correct
4. A helpful hint for the learner
''',

    "part3": '''
TOEIC Listening Part 3: Conversations

Create a conversation scenario similar to TOEIC Part 3 on the topic: given by user. In this part:
- The audio contains a conversation between 2-3 speakers.
- Each conversation is followed by 3 questions, each with 4 answer options (A, B, C, D).
- The questions test understanding of main ideas, details, inferences, and speaker purpose.

Guidelines:
- Create a natural workplace or everyday conversation between 2-3 speakers.
- Clearly label speakers (e.g., Man, Woman, Narrator).
- Conversation should be 30-45 seconds long (approximately 8-12 exchanges).
- Develop 3 questions that test different aspects of listening comprehension.
- Each question should have 4 answer options with only one correct answer.
- Incorrect options should be plausible but not accurate based on the conversation.

Difficulty levels:
- Easy: Clear speakers, simple vocabulary, questions focused on explicitly stated information
- Medium: Some specialized vocabulary, questions requiring simple inference, moderate pace
- Hard: Complex vocabulary, questions requiring significant inference, idiomatic expressions

Return a JSON object with:
1. A brief context setting for the conversation
2. The full transcript of the conversation (this is the audio transcript)
3. Three questions about the conversation, each with four options (mark which one is correct)
4. A general hint to help learners understand the conversation
''',

    "part4": '''
TOEIC Listening Part 4: Short Talks

Create a short talk/monologue similar to TOEIC Part 4 on the topic given by user. In this part:
- The audio contains a monologue (announcement, advertisement, news report, or short talk).
- Each talk is followed by 3 questions, each with 4 answer options (A, B, C, D).
- The questions test understanding of main ideas, specific details, and implied information.

Guidelines:
- Create a coherent, natural-sounding monologue on a workplace or general topic.
- Talk should be 45-70 seconds long (approximately 150-200 words).
- Content should be informative and realistic (announcement, news, report, speech, etc.).
- Develop 3 questions that test different aspects of listening comprehension.
- Each question should have 4 answer options with only one correct answer.
- Incorrect options should be plausible but not accurate based on the talk.

Difficulty levels:
- Easy: Clear structure, common vocabulary, questions about explicit information
- Medium: More specialized vocabulary, some implied information, moderate complexity
- Hard: Technical vocabulary, questions requiring significant inference, complex ideas

Return a JSON object with:
1. A brief context setting for the talk
2. The full transcript of the talk (this is the audio transcript)
3. Three questions about the talk, each with four options (mark which one is correct)
4. A general hint to help learners understand the talk
'''
}

if __name__ == "__main__":
    conservation_question = QuestionGenerator(TOEICListeningQuestion)
    response = conservation_question.generate_question({"description": TOEIC_PROMPTS['part4'],
                                            "topic": "work"})
    with open("part4_1.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4, ensure_ascii=False) 
    # print(response)