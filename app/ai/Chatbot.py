import yaml
from typing import List, Dict, Literal, Union, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage,SystemMessage
from app.ai.LLMFactory import LLMFactory
from sqlalchemy.orm import Session
from app.models.messaging import ConversationMessages

from app.db.session import get_db

class ChatResponse(BaseModel):
    messages: List[str] = Field(description="List of messages to display sequentially")
    suggestions: List[str] = Field(description="3 suggested responses for the user")

class ChatHistory(BaseModel):
    role: Literal["human", "assistant"]
    content: str
    timestamp: str
class Chatbot:
    def __init__(self, config_path: str = "/app/ai/config.yaml", history_limit: int = 20):
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        self.history_limit = history_limit
        self.llm = LLMFactory.create_llm(self.config, provider='google', type='chat')
        self.parser = JsonOutputParser(pydantic_object=ChatResponse)
        
        # Template that includes chat history
        self.template = """You are a friendly English learning assistant chatbot. Respond naturally like in daily chat messages, using short messages, casual language, and sometimes internet slang/abbreviations when appropriate.

Keep responses conversational and avoid lengthy explanations. Split longer responses into multiple short messages.

For topics outside English learning, briefly suggest where to find more information instead of explaining everything.

Previous conversation history:
{chat_history}

Human message: {message}

Format your response as JSON with:
1. messages: Array of short messages to display sequentially
2. suggestions: Array of 3 natural suggested responses the user could reply with

{format_instructions}
"""
        self.prompt = ChatPromptTemplate.from_template(
            template=self.template,
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain =self.prompt| self.llm | self.parser

    def format_chat_history(self, history) -> str:
        """Format chat history into a string."""
        formatted = []
        for msg in history:  # Only take last N messages
            role = "Human" if msg['role'] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

# Function to process the sentence
    def generate_response(self,sentence: str,db: Session,current_user_id):
        try:
            # Try to get the response
            chat_history = self.get_chat_history(db,current_user_id)
            # print(chat_history)
            chat_history_formatted = self.format_chat_history(chat_history)
            # print(chat_history_formatted)
            result = self.chain.invoke({"message": sentence,
                                        "chat_history":chat_history_formatted,
                                        })
            return result
        except Exception as e:
            # Log the error (implement your logging mechanism)
            print(f"Error generating response: {str(e)}")
            
            # Return a fallback response
            return ChatResponse(
                messages=["I apologize, but I'm having trouble processing your request right now. Could you try rephrasing your message?"],
                suggestions=[
                    "Could you explain that differently?",
                    "Let's try a simpler question",
                    "Can we start over?"
                ]
            )
    def get_chat_history(self, db: Session,current_user_id):
        try:
            history = (db.query(ConversationMessages)
                    .filter(ConversationMessages.user_id == current_user_id)
                    .order_by(ConversationMessages.created_at.desc())
                    .limit(self.history_limit)
                    .all())
            return [
                    {
                        "role": row.sender,
                        "content": row.content,
                        "timestamp": row.created_at
                    }
            for row in history] 
            
        except Exception as e:
            # Log the error
            print(f"Error retrieving history: {str(e)}")
            return []
        

# Example usage
if __name__ == "__main__":
    chatbot = Chatbot()
    response = chatbot.generate_response('Hello, I have been standing here since this afternoon!')
    print(response)