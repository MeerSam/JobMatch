from sentence_transformers import SentenceTransformer

# Load pretrained BERT model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_st_embedding(text):    
    embedding = model.encode(text, convert_to_tensor=True)
    return embedding