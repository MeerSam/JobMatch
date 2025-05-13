import json
import logging
from db.data_models import  JobResponseModel, ResumeResponseModel, AnalysisResponseModel
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import AIMessage

from db.db_connector import get_database
from db.dboperations import MongoDBOperationHandler
from utils.constants import JOBDESC_PARSER,ANALYZER_SYSTEM_PROMPT, RESUME_EXTRACT_PROMPT
 
class ResumeParserChain:
    """ Chain for parsing resume""" 
    def __init__(self, llm ):  
        self.parser = PydanticOutputParser(pydantic_object=ResumeResponseModel)
        # Implementation of document parsing chain 
        prompt =  PromptTemplate(
            template= RESUME_EXTRACT_PROMPT,
            input_variables=["resume_data"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        ) 
        self.prompt = prompt         
        self.chain =  (prompt | llm )

    def run(self, resume_data):
        """ Returns a dictionary with following
        response : Original response from LLM
        data: dictionary of databse saved items along with db.collection("yourcollection_name")._Id
        
        """
        try:
            # Run the matching analysis 
            self.raw_resume = resume_data  
            response = self.chain.invoke(resume_data)  
            if isinstance(response, AIMessage):
                #####print("This is an AIMessage!")
                #####print("Resume Content:", response.content)
                response = response.content.strip("\n")               
            elif isinstance(response, str):
                #####print(f"ResumeParserChain.Response is not an AIMessage. Content: \n {response}")
                response.strip("\n")
            if isinstance(response, str):
                response = response.strip() 
            return self.next_steps(response)
        except Exception as e:
            logging.error(f"ResumeParserChain Error: {e}")
            raise

    async def arun(self, resume_data):
        """ Returns a dictionary with following
        response : Original response from LLM
        data: dictionary of databse saved items along with db.collection("yourcollection_name")._Id        
        """
        try:
            # Run the matching analysis 
            self.raw_resume = resume_data   
            response = await self.chain.ainvoke(resume_data)  
            if isinstance(response, AIMessage):
                #####print("ResumeParserChain.This is an AIMessage!")
                #####print("Content:", response.content)
                response = response.content.strip("\n")               
            elif isinstance(response, str):
                #####print(f"ResumeParserChain.Response is not an AIMessage. Content: \n {response}")
                response.strip("\n")
            if isinstance(response, str):
                response = response.strip()  
            return self.next_steps(response) 
        except Exception as e:
            logging.error(f"ResumeParserChain.Error: {e}")
            raise 
    
    def next_steps(self, response):
        response = response.strip()
        self.resume_json = response
        ret_data = None
        self.resume_id = None
        response_dict = None
        ret_results =   {"response": response,
                            "data" : ret_data} 
        try:            
            response_dict = json.loads(response) 
        except Exception as e:
            pass
        try:
            resume_model_data = None 
            resume_model_data = self.parser.parse(response)  
             
        except Exception as e:
            logging.error(f"ResumeParserChain next_steps: Error while parsing output: {e}")

        try:
            response_dict['resume_response']=response
            ret_data = self.save_resume_resonse(response_dict) 
            self.resume_json = response 
            if self.resume_id is None :
                self.resume_id = ret_data.get("resume_id")             
            return {"response": response,
                    "data" : ret_data}
        except Exception   as e:
            logging.error(f"resume: next_steps:Error during saving resume(1) data {e}")
        try:
            ret_data =self.save_resume_resonse(response)
            return {"response": response,
                "data" : ret_data}
        except Exception as e:
            logging.error(f"resume: next_steps:Error during saving resume(2) data {e}")
        return {"response": response,
                "data": ret_data}

    def save_resume_resonse(self, data):
        """
        Saves parsed resume data to multiple MongoDB collections.
        """
        try: 
            data['raw_resume'] = self.raw_resume
            data['resume_json'] = self.resume_json
            resume_data = {"collection_name": "resume",
                           "upsert_identifiers" : { "email" : data.get("email")}, 
                            "data": data }
            
            data_collection = [resume_data ]
            db = get_database()
            if db is not None:
                objdbservice = MongoDBOperationHandler(db)
                results = objdbservice.save_data_to_db(data_collection if type(data_collection) == list else [data_collection])
                if results is not None and len(results)> 0:
                    self.resume_id = results[0].get("Id")

                data['resume_id'] = self.resume_id
        except Exception as e:
            logging.error(f"ResumeParserChain.save_resume_resonse: {e}")
        return data

class JobDescParserChain:
    """ Chain for parsing job description"""

    def __init__(self, llm):
        self.llm =llm
        self.parser = PydanticOutputParser(pydantic_object=JobResponseModel)
        # Implementation of document parsing chain 
        prompt =  PromptTemplate(
            template= JOBDESC_PARSER,
            input_variables=["job_description"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        ) 
        self.prompt = prompt         
        self.chain =  (prompt | self.llm )

    def run(self, job_description):
        # Run the matching analysis     
        try:
            self.raw_jobdesc = job_description   
            response = self.chain.invoke(job_description) 
            if isinstance(response, AIMessage):
                #####print("This is an AIMessage!")
                #####print("JobDescParserChain Content:", response.content)
                response = response.content.strip("\n")               
            elif isinstance(response, str):
                #####print(f"JobDescParserChainResponse is not an AIMessage. Content: \n {response}")
                response.strip("\n")
            if isinstance(response, str):
                response = response.strip()  
            return self.next_steps(response)
        except Exception as e:
            logging.error(f"Error: {e}")
            raise

    async def arun(self, job_description):
        # Run the matching analysis     
        try:
            self.raw_jobdesc = job_description   
            response = await self.chain.ainvoke(job_description)
            if isinstance(response, AIMessage):
                # #####print("JobDescParserChainThis is an AIMessage!")
                #####print("JobDescParserChain Content:", response.content)
                response = response.content.strip("\n")               
            elif isinstance(response, str):
                #####print(f"JobDescParserChain Response is not an AIMessage. Content: \n {response}")
                response.strip("\n")
            if isinstance(response, str):
                response = response.strip() 
            return self.next_steps(response)  
        except Exception as e:
            logging.error(f"Error: {e}")
            raise 

    def next_steps(self, response): 
        self.jobdesc_json = response
        ret_data = None
        self.job_id =   None 
        ret_results =   {"response": response,
                            "data" : ret_data}
        try:
            response_dict = None
            response_dict = json.loads(response) 
        except Exception as e:
            pass
        try:
            jd_model_data = None
            jd_model_data = self.parser.parse(response)  
        except Exception as e:
            logging.error(f"jd: next_steps: Error while parsing output: {e}")
        try:
            response_dict['job_response']=response
            ret_data = self.save_jobdesc_resonse(response_dict ) 
            if self.job_id is None :
                self.job_id = ret_data.get("job_id")
            ret_results = {"response": response,
                    "data" : ret_data}
            return ret_results 
        except Exception   as e:
            logging.error(f"job desc next_steps:Error during saving job desc(1) data {e}")
        try:
            ret_data =self.save_jobdesc_resonse(response)
            return {"response": response,
                "data" : ret_data}
        except Exception as e:
            logging.error(f"next_steps:Error during saving job desc(2) data {e}")
        return {"response": response,
                "data": ret_data}
    
    def save_jobdesc_resonse(self, data):
        try:
            # job_data response
            data['raw_jobdesc'] = self.raw_jobdesc
            data['jobdesc_json'] = self.jobdesc_json
            job_datainfo = {"collection_name": "job",
                            "upsert_identifiers" : { "external_job_id" : data.get("external_job_id")}, 
                            "primary_key" : "external_job_id",
                            "data": data
                            } 
            data_collection = [job_datainfo] 
            db = get_database()
            if  db is not None:
              objdbservice = MongoDBOperationHandler(db)
              dbresults  = objdbservice.save_data_to_db(data_collection if type(data_collection) == list else [data_collection])
              if dbresults is not None and len(dbresults)> 0:
                self.job_id = dbresults[0].get("Id")
              data['job_id'] = self.job_id
        except Exception as e:
            logging.error(f"save_jobdesc_resonse: {e}")
        return data 

class AnalyzerChain:
    """ Chain that Matches the resume and jobdescriptions and outputs results"""
    def __init__(self, llm ):
        self.llm = llm   
        self.parser = PydanticOutputParser(pydantic_object=AnalysisResponseModel)
        # Implementation of document parsing chain 
        prompt =  PromptTemplate(
            template= ANALYZER_SYSTEM_PROMPT,
            input_variables=["resume_data", "job_description"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        ) 
        self.prompt = prompt         
        self.chain =  (prompt | llm )

    def run(self, resume_data, job_description, resume_id=None, job_id=None):        
        # Run the matching analysis  
        ret_results = {"response": None,
                            "data" : None}
        try:     
            try:
                self.resume_id = resume_id     
                self.job_id = job_id  
            except Exception as e:
                #####print(f"Error resume_id({resume_id})/jobid({job_id}) : {e}")  
                logging.error(f"Error resume_id({resume_id})/jobid({job_id}) : {e}")  

            response = self.chain.invoke(input= {"resume_data": resume_data, "job_description": job_description})
            #AIMessage
            if isinstance(response, AIMessage):
                # #####print("This is an AIMessage!")
                #####print("Content:", response.content)
                response = response.content.strip("\n")               
            elif isinstance(response, str):
                #####print(f"Response is not an AIMessage. Content: \n {response}")
                response.strip("\n")
            response = response.strip()   
            return self.next_steps(response)
        except Exception as e: 
            logging.error(f"Error: {e}")
            raise 
    
    async def arun(self, resume_data, job_description, resume_id, job_id):        
        # Run the matching analysis          
        try: 
            response = None    
            try: 
                self.resume_id = resume_id     
                self.job_id = job_id  
                print(f"\n\nAnalyzerChain-resume_id({resume_id})\n\njobid({job_id})")
            except Exception as e:
                print(f"\n\nAnalyzerChain-Error resume_id({resume_id})/jobid({job_id}) : {e}")  
                logging.error(f"Error resume_id({resume_id})/jobid({job_id}) : {e}")  

            response = await self.chain.ainvoke(input= {"resume_data": resume_data, "job_description": job_description})
            #AIMessage
            if isinstance(response, AIMessage):
                print("This is an AIMessage!")
                #####print("Content:", response.content)
                response = response.content.strip("\n")               
            elif isinstance(response, str):
                #####print(f"Response is not an AIMessage. Content: \n {response}")
                response.strip("\n")
            if isinstance(response, str):
                response = response.strip() 
            return self.next_steps(response)
        except Exception as e: 
            logging.error(f"Error: {e}")
            raise 

    def next_steps(self, response):
        try: 
            self.match_json = response
            ret_data = None
            ret_results = {"response": response,
                            "data" : ret_data}            
            try:
                response_dict = None
                response_dict = json.loads(response) 
            except Exception as e:
                logging.error(f"Error parsing output. convert to dict: {e}")
            try:
                match_model_data = None 
                match_model_data= self.parser.parse(response)
            except Exception as e:
                #####print(f"Error parsing output: {e}")
                logging.error(f"Error parsing output: {e}")
            try:
                response_dict['match_response']=response
                ret_data = self.save_evaluation_results(response_dict)
                ret_results = {"response":  response,
                        "data" : ret_data}
                return ret_results
            except Exception as e:
                #####print(f"Error saving output: {e}")
                logging.error(f"Error saving output: {e}")

                try:
                    ret_data = self.save_evaluation_results(match_model_data.model_dump())
                    ret_results = {"response":  response,
                        "data" : ret_data}
                    return ret_results
                except Exception as e:
                    logging.error(f"Error during Anlyzing and saving match data {e}")
            return {"response": response}
        except Exception as e: 
            logging.error(f"Error: {e}")
            raise 
        
        
    def save_evaluation_results(self, result_data):
        try: 
            collection_name =  "jobmatch_result"             
            if  self.resume_id :
                result_data["resume_id"] = self.resume_id 
            if  self.job_id   : 
                result_data["job_id"] = self.job_id 
            if self.job_id and self.resume_id:   
                upsert_identifiers = {
                    "resume_id" : self.resume_id,
                    "job_id" : self.job_id
                }
            else:
                upsert_identifiers = {}

            # Save the result data to the database  
            #####print(f"save_evaluation_results: {result_data}")
                # Fall back if IDs are not available
            match_data ={"collection_name": "jobmatch_result", 
                         "upsert_identifiers": upsert_identifiers, 
                         "data": result_data }
            data_collection = [match_data ]
            db = get_database()
            if db is not None:
              obj_dbservice = MongoDBOperationHandler(db)
              dbresults  = obj_dbservice.save_data_to_db(data_collection if type(data_collection) == list else [data_collection])
            if dbresults is not None and len(dbresults)> 0:
                self.match_id = dbresults[0].get("Id") 
            result_data['match_id'] = self.match_id
            return result_data
        except Exception as e:
            print(f"Error during save_evaluation_results : {e}")   
