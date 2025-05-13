import os, sys, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()

def get_tfidfvectors(docs:list):
    vectors = vectorizer.fit_transform(docs)
    return vectors
    