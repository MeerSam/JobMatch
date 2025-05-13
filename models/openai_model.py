import openai
import os
from langchain_openai import ChatOpenAI

from models.llmProvider import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name="gpt-4", temperature=0, api_key=None ,max_tokens = 2000,verbose=False):
        self.model_name = model_name 
        self.temperature = temperature
        self.api_key = api_key
        
    def get_llm(self):
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )
    
def run_openai(resume_text):
    response = openai.create( model="gpt-4-turbo", #            model="gpt-4",
        messages=[{"role": "system", "content": f"Extract relevant skills:\n\n{resume_text}"}]
    )
    return response["choices"][0]["message"]["content"]
  
def get_openai_embedding(text):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"  # OpenAI's embedding model
    )
    return response.data[0].embedding 
