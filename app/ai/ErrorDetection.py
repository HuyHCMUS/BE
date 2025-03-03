import yaml
from app.ai.LLMFactory import LLMFactory
from typing import List, Dict, Literal, Union
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import  JsonOutputParser
from pydantic import BaseModel, Field

# Define the output schema
class Error(BaseModel):
    error_segment: str = Field(description="The part of sentence containing error")
    suggestion: str = Field(description="Correction suggestion")
    error_type: Literal["Grammar", "Vocabulary", "Spelling", "Word Choice", "Sentence Structure"] = Field(
        description="Type of error"
    )

class Vocabulary(BaseModel):
    original: str = Field(description="Original Vietnamese word/phrase")
    suggestion: str = Field(description="English translation")

class SentenceAnalysis(BaseModel):
    corrected_sentence: str = Field(description="Fully corrected English sentence")
    errors: List[Error] = Field(description="List of errors found in the sentence")
    vocabulary: List[Vocabulary] = Field(description="List of Vietnamese-English translations")

class ErrorDetection:
    def __init__(self, config_path: str = "/app/ai/config.yaml"):

        self.config = {}
        self.llm = LLMFactory.create_llm(self.config,provider ='google',type='llm')
        self.parser = JsonOutputParser(pydantic_object=SentenceAnalysis)
        self.template = """You are an English teaching assistant. Analyze the following English-Vietnamese mixed sentence and provide corrections:

{input_sentence}

{format_instructions}

If the sentence has no errors, respond with exactly "OK".
Otherwise, provide the analysis in the specified JSON format."""

        self.prompt = PromptTemplate.from_template(
                    template=self.template,
                    partial_variables={"format_instructions": self.parser.get_format_instructions()}
                )
        self.chain = self.prompt | self.llm | self.parser

    # Function to process the sentence
    def analyze_sentence(self,sentence: str) -> Union[str, Dict]:
        try:
            # Try to get the analysis
            result = self.chain.invoke({"input_sentence": sentence})
            return result
        except Exception as e:
            # If we get "OK", it will raise an error when parsing JSON
            if "OK" in str(e):
                return None
            # For other errors, raise them
            else:
                return 'Error generating response: ' + {str(e)}
        
if __name__ == "__main__":
    corrector = ErrorDetection()
    response = corrector.analyze_sentence('I stand here từ chiều!')
    print(response)