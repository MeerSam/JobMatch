import os
from functools import lru_cache 
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi 

@lru_cache()
def get_database():
    """Get MongoDB connection (cached to avoid multiple connections)""" 
    mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/") 
    # MongoDB connection
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))  

    try:
       # Get database
        db_name =  os.environ.get("MONGO_DB", "resume_analyzer")
        return client[db_name]
    except Exception as e: 
        return ValueError(f"Error connecting to database. {e}")
