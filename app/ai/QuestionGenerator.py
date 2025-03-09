import yaml
from app.ai.LLMFactory import LLMFactory
from typing import List, Dict, Literal, Union
from langchain_core.prompts import PromptTemplate


from langchain_core.output_parsers import  JsonOutputParser
from pydantic import BaseModel, Field

class QuestionGenerator:
    def __init__(self,parser,config_path: str = "config.yaml"):
        self.config = {}

        self.llm = LLMFactory.create_llm(self.config,provider ='google',type='llm')
        self.parser = JsonOutputParser(pydantic_object=parser)
        
        self.template = '''
You are a professional assistant specialized in generating English questions for learners. Your task is to create questions based on the provided information.

## Question Type:  
{question_type_description}  

## The question content may belong to the following topics:  
{topic}  

## Requirements:
- Generate questions that align with the description above.  
- Format the output according to the instructions below.  

## Output Format:  
{format_instructions}  

Please return only the result without any explanations.
'''
        self.prompt = PromptTemplate.from_template(
                    template=self.template,
                    partial_variables={"format_instructions": self.parser.get_format_instructions()}
                )
        self.chain = self.prompt | self.llm | self.parser

    def generate_question(self, question_info):
        try:
            input_text = self.prompt.format(
                question_type_description=question_info['description'],
                topic=question_info['topic']
            )


            # Gọi model để tạo câu hỏi
            result = self.chain.invoke({
                "question_type_description": question_info['description'],
                "topic": question_info['topic']
            })
            return result
        except Exception as e:
            return 'Error generating question: ' + str(e)
        


    
