from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, List, Any
import os
from db.db_connector import get_database

class MongoDBOperationHandler: 
    def __init__(self, db, verbose=False):
        self.db_name = db
        self.verbose =verbose 

    def initialize(self):
        try: 
            collection_names = ["resume", "job" , "jobmatch_result", "jobs_list", "candidates_list"]
            existing_collections = self.db_name.list_collection_names()
            for col_name in collection_names:
                if col_name not in existing_collections:
                    collection = self.db_name.create_collection(col_name)
                    if self.verbose:
                        print(f"Collection '{col_name}' created!")
                        pass
                else:
                    collection = self.db_name.get_collection(col_name)
                    if self.verbose:
                        print(f"Collection '{col_name}' already exists.")
                        pass

                if collection.name == "resume":
                    index_name ="resume_index"
                    pk_constraints = [("email", 1)]
                    self.create_new_indexes(collection, index_name, pk_constraints)
                    
                elif collection.name == "job":
                    index_name ="job_index"
                    pk_constraints = [("external_job_id", 1)]
                    self.create_new_indexes(collection, index_name, pk_constraints) 

                elif collection.name == "jobmatch_result": 
                    index_name ="resume_job_index"
                    pk_constraints =[("resume_id", 1), ("job_id", 1)]
                    self.create_new_indexes(collection, index_name, pk_constraints)  
            if self.verbose:
                #####print(f"MongoDB Initialization completed")
                pass
        except Exception as e:
            print(f"Error in MongoDB initialization: {e}")
            pass

    def create_new_indexes(self, collection, index_name, pk_constraints):
        try: 
            # Check if index exists
            existing_indexes = collection.index_information()
            if index_name not in existing_indexes:                    
                collection.create_index(pk_constraints, unique=True, name=index_name)
                if self.verbose:
                    print(f"Unique index created {index_name} for collection  : {collection.name}!")
                    pass

            else:
                if self.verbose:
                    print(f"{index_name}: Index already exists for collection  : {collection.name}, skipping creation.")
                    pass
        except Exception as e:
            print(f"Error creating index {index_name} for collection {collection.name}: {e}")
            pass
         
    def save_data_to_db(self, table_collections: List):
        """
        Save parsed and extracted database collection data to MongoDB.
        """
        retResults = []
        try:
            
            if table_collections is not None  :
                for table_info in table_collections: 
                    collection = None
                    pk = table_info.get("primary_key")                    
                    data = table_info.get("data")
                    pk_value = data.get(pk) 
                    upsert_identifiers = {}
                    if pk is not None :
                        upsert_identifiers = {pk: pk_value}
                    else:
                        upsert_identifiers = table_info.get("upsert_identifiers") 
                    collection = self.db_name.get_collection(table_info.get("collection_name")) 
                    if upsert_identifiers is None:
                        return {"status": "failed", "reason": f"Missing primary key in {table_info.get('collection_name')} data"}

                    # Use email as the primary key contraint not as _id
                    #data["_id"] = pk_value
                    if collection is not None:
                        # upsert or update the resume in MongoDB 
                        result = collection.update_one(upsert_identifiers, {"$set": data}, upsert=True) 
                        record_id =None
                        if result.upserted_id:
                            record_id = result.upserted_id  
                            message = f"New document inserted with _id: {result.upserted_id}"
                            #####print(message)
                        else:
                            doc = collection.find_one(upsert_identifiers)
                            record_id = doc['_id']
                            message =f"Existing record _id: {doc['_id']}"
                            #####print(message)

                        retResults.append({"status": "success", 
                                           "message":  f"Data saved for {collection.name}({pk_value}) : {record_id}",
                                           "Id" : record_id})
        except Exception as e:
            print(f"Error in DBOperations save_data_to_db: {e}")
        return retResults
                      
    def update_collection(self, collection,  update_data ):
        """
            Update Collection with extra data.
        """
        retResults = []
        try:
            data =  update_data.get("data")
            data_Id =update_data.get("_id")
            # Update the resume document
            result = collection.update_one({"_id": data_Id}, data)  
            retResults.append({"status": "success", 
                                           "message":  f"Data saved for {collection.name}({data_Id}) : {result.inserted_id}",
                                           "Id" : result.inserted_id})
        except Exception as e:
            if self.verbose:
                print(f"Error in DBOperations update_collection: {e}")
        return retResults

    def get_record(self, collection_name, filter, projection:dict={}):
        try: 
            collection = self.db_name.get_collection(collection_name) 
            doc = collection.find_one(filter)
            return doc if doc else None 
        except Exception as e:
            print(f"Error in DBOperations get_record: {e}")

    def get_records(self, collection_name, filter={} ): 
        try: 
            collection = self.db_name.get_collection(collection_name) 
            doc = collection.find(filter) 
            return doc if doc else None 
        except Exception as e:
            print(f"Error in DBOperations get_records: {e}")
if __name__=="__main__":
    db = get_database()
    existing_collections = db.list_collection_names()
    #####print(existing_collections)
    # wrong_collection = db.get_collection("jobjobmatch_result")
    # wrong_collection.drop_indexes()
    # db.drop_collection(wrong_collection)
    Mongo = MongoDBOperationHandler(db, True)
    # Mongo.initialize()
    data = {"collection_name": "resume",
                              "primary_key" : "email",
                              "data": {
                                  "name" : "Test Resume",
                                  "email" : "Testter@testing.com",
                                  "phone" : "555-987-1234",
                                  "raw_resume": """tester Resume
                                  Great at everything
                                  """
                              } } 
    collection =db.get_collection("resume")
    query = {"email": "Testter@testing.com"}
    result = collection.find_one(query)
    #####print(result)
    # #####print(Mongo.save_data_to_db( [data]))


# collection.find(
#     filter={},                 # Query criteria
#     projection=None,           # Fields to include/exclude
#     skip=0,                    # Number of documents to skip
#     limit=0,                   # Maximum number of results
#     sort=None,                 # Sort criteria
#     hint=None,                 # Index hint
#     allow_partial_results=False,  # For sharded clusters
#     batch_size=0,              # Number of documents per batch
#     return_key=False,          # Return only index keys
#     show_record_id=False,      # Show record ID
#     max_time_ms=None,          # Max execution time
#     comment=None,              # Query comment
#     collation=None             # Collation options
# )
# # Skip first 10 results and limit to 5
# collection.find({}).skip(10).limit(5)

# results = collection.find(
#     {"age": {"$gte": 25}},                  # Filter: age >= 25
#     {"name": 1, "email": 1, "_id": 0},      # Projection: return only name and email
# ).skip(10).limit(5).sort("name", 1)         # Pagination and sorting

# for doc in results:
#     #####print(doc)