from models.bedrock_model import  get_bedrock_embedding
from models.openai_model import  get_openai_embedding
from models.sentencetransformer_model import get_st_embedding
from models.tfidf_model import get_tfidfvectors

import numpy as np

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


class EmbeddingModel:
    def __init__(self, model_type="bedrock"):
        if model_type == "bedrock-embedding":
            self.embed_func = get_bedrock_embedding 
        elif model_type == "openai_embedding":
            self.embed_func = get_openai_embedding
        elif model_type == "TfidfVectorizer":
            # Better for keyword match : same words
            self.embed_func = get_tfidfvectors
        elif model_type == "sentence_transformer":
            # better for semantic matching
            self.embed_func = get_st_embedding
        else:
            raise ValueError(f"Invalid model type: Choose 'bedrock' or 'openai'. given {model_type}")

    def get_embedding(self, input):
        return self.embed_func(input)
    
     


if __name__ == "__main__":
    embedding_model = EmbeddingModel(model_type="sentence_transformer")  # Change to "openai_embedding" to switch 
    resume_text = "Python, FastAPI, AWS experience"
    job_text = "Hiring for an AWS developer with Python expertise"

    resume_embedding = embedding_model.get_embedding(resume_text)
    job_embedding = embedding_model.get_embedding(job_text)

    similarity_score = cosine_similarity(resume_embedding, job_embedding)
    #####print(f"Similarity Score: {similarity_score}")
 