from abc import ABC,abstractmethod
import os, time


from fastapi import HTTPException
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate 
from langchain_core.output_parsers import StrOutputParser 
from langchain_openai import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# Custom imports from my project
from models.bedrock_model import run_bedrock, get_bedrock_embedding
from models.openai_model import run_openai, get_openai_embedding
from models.openai_model import OpenAIProvider
from models.bedrock_model import BedrockProvider
from models.similarity_model import EmbeddingModel
from models.spacy_model import nlp 
 
USE_BEDROCK = os.environ.get("USE_BEDROCK", "False").lower() == "true"
 

langchain_chat_kwargs = {
    "temperature": 0,
    "max_tokens": 4000,
    "verbose": True,
}

class ModelRegistry:
    """Singleton class to store all processing models"""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance.models = {}
            cls._instance.loaded = False
        return cls._instance 
    
    def __init__(self):
        self.loaded = False 
        self.loading = False

    def load_all_models(self):
        """Load all models during app startup"""
        if self.loaded:
            return
        start_time = time.time() 
        self.loading = True
        #####print("Loading NLP models...")
        # Global model objects
        self.nlp_models = {} 
        # Using LangChain Openai/bedrock
        if USE_BEDROCK:
            llm_provider = BedrockProvider(
                model_id=os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
                region_name=os.environ.get("AWS_REGION", "us-east-1"),
                temperature= os.environ.get("TEMP",0)
            )
        else:
            llm_provider = OpenAIProvider(
                model_name=os.environ.get("OPENAI_MODEL", "gpt-4"),
                api_key=os.environ.get("OPENAI_API_KEY"),
                **langchain_chat_kwargs
            )
        # Initialize LLM 
        self.nlp_models["llm"] = llm_provider.get_llm()

        # Initialize embeddings model - sentence_transformers
        self.nlp_models["st_embeddings"] = EmbeddingModel(model_type=os.environ.get("EMBEDDING_MODEL", "sentence-transformers"))
        #self.nlp_models.get("st_embeddings", EmbeddingModel(model_type="openai_embedding")).get_embedding(text)
        #OPEN_API_KEY - loads from environment variable


        # Initialize embeddings model - OpenAIEmbeddings
        self.nlp_models["embeddings"] = OpenAIEmbeddings()
        
        # Initialize TF-IDF model
        self.nlp_models["tfidf_model"] = EmbeddingModel(model_type="TfidfVectorizer")

        # Initialize nlp_tool : spacy / ner_tool: transformer.pipeline
        if os.environ.get('NLP_TOOL').lower() =='spacy':
            self.nlp_models["nlp_tool"] = {'name': 'spacy',
                                    'tool': nlp} 
            # self.nlp_models["nlp_tool"] = {'name': 'ner_tool',
            #                           'tool': ner_pipeline}
        else:
            self.nlp_models["nlp_tool"] = {'name': 'spacy',
                                    'tool': nlp} 
        

        # Load any other heavy ML/NLP models here
        llm=self.nlp_models["llm"] 

        self.loaded = True
        self.loading = False
        #####print(f"All models loaded in {time.time() - start_time:.2f} seconds")

    def get_model(self, model_name):
        """Get a specific model by name"""
        if not self.loaded:
            raise RuntimeError("Models not loaded yet")
        return self.nlp_models.get(model_name)
    
    def get_models(self):
        """Get a dictionary model"""
        if self.loading:
            raise HTTPException(status_code=503, detail="Models not loaded yet. wait for models to load")
        else:
            if not self.loaded:
                raise HTTPException(status_code=500, detail="Models failed to load")
        return self.nlp_models

    def cleanup(self):
        self.nlp_models.clear()

class ModelLoader:
    def __init__(self, model_type: str):
        if model_type == "bedrock": 
            self.model_func = run_bedrock
        elif model_type == "openai": 
            self.model_func = run_openai
        else:
            raise ValueError("Unsupported model type. Choose 'bedrock' or 'openai'.")
        pass
    
# Create a global instance
model_registry = ModelRegistry()
