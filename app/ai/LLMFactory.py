from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain_community.llms import HuggingFaceHub
# from langchain.llms.huggingface_pipeline import HuggingFacePipeline
import os


class LLMFactory:
    @staticmethod
    def create_llm(config: dict,provider = 'google', model='gemini-2.0-flash' ,type ='chat'):
        temperature = config["llm"].get("temperature", 0.7)
        max_tokens = config["llm"].get("max_tokens", 4096)

        if provider == "openai":
            return ChatOpenAI(
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider == "huggingface":
            return HuggingFaceHub(
                repo_id=model,
                model_kwargs={"temperature": temperature, "max_length": max_tokens}
            )
        elif provider == 'google':
            if type =='llm':
                os.environ["GOOGLE_API_KEY"] = "AIzaSyAJCAzt_4sAKIwWJuhdYWynBZmHt2GSNGg"
                return GoogleGenerativeAI(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens)
            else:
                os.environ["GOOGLE_API_KEY"] = "AIzaSyAJCAzt_4sAKIwWJuhdYWynBZmHt2GSNGg"
                return ChatGoogleGenerativeAI(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens)
        # elif provider == "selfhosted":
        #     from transformers import pipeline
        #     pipe = pipeline("text-generation", model=model)
        #     return HuggingFacePipeline(pipeline=pipe)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
