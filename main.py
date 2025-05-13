import json
import sys
import os
from typing import Dict
from pydantic import BaseModel
import uvicorn  
from bson import json_util 

from db.data_models import DataModel
from db.db_connector import get_database
from services.candidatematch_agent import CandidateFinderAgent
from services.dataservices import JobDataService, ResumeDataService, ResumeJobMatchDataService
from services.jobfinder_agent import JobFinderAgent


# Add the project root directory to Python's module search path
sys.path.append(os.path.abspath(os.path.dirname(__file__))) 
from fastapi import Depends, FastAPI, File, UploadFile 
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware 
from contextlib import asynccontextmanager

# Custom imports from my projects
from models.model_loader import model_registry
from services.docparser import MatchKeywordsService
from services.file_parser import FileParser, create_temp_file
from services.analyzer_agent import ResumeAnalyzerAgent

# Load environment variables
load_dotenv()

USE_BEDROCK = os.environ.get("USE_BEDROCK", "False").lower() == "true"
LLM_MODEL_TYPE = 'bedrock' if USE_BEDROCK else 'openai'

origins = [
    "http://localhost:3000",  # Example frontend URL
    "https://yourdomain.com",
    "http://localhost:8501"
]

# Initialize components based on configuration 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    """Load all NLP models at application startup"""
    model_registry.load_all_models()
    #agent = ResumeAnalyzerAgent(model_registry.get_model("llm"))
    yield
    # Clean up the ML models and release the resources
    # For example, a database connection pool, or loading a shared machine learning model.
    model_registry.cleanup()

app = FastAPI(title="Resume Analyzer API",lifespan=lifespan) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

async def get_file_parser():
    return FileParser()

async def get_kw_extraction_service():
    return MatchKeywordsService( nlp_tool= model_registry.get_model("nlp_tool"),
                                  vectorizer= model_registry.get_model("tfidf_model"),
                                  embedding_model=model_registry.get_model("st_embeddings"))

async def get_agent_analyzer():
    return ResumeAnalyzerAgent(llm=model_registry.get_model("llm"))

async def get_candidate_finder_agent():
    db = get_database()
    if db is None:
        raise ValueError("Database connection not initialized")
    return CandidateFinderAgent(llm=model_registry.get_model("llm"), db=db)

async def get_job_finder_agent():
    db = get_database()
    if db is None:
        raise ValueError("Database connection not initialized")
    return JobFinderAgent(llm=model_registry.get_model("llm"), db=db)

# Following endpoints 
@app.get("/")
def read_root():
    return {"message": "Welcome to Resume Analyzer and Scoring API"} 

@app.get("/provider-info/")
async def get_provider_info():
    """Get information about the current LLM provider"""
    if USE_BEDROCK:
        return {
            "provider": "AWS Bedrock",
            "model": os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        }
    else:
        return {
            "provider": "OpenAI",
            "model": os.environ.get("OPENAI_MODEL", "gpt-4")
        }

@app.post("/analyze-resume/")
async def analyzer(resume_file:UploadFile = File(...), 
                        jobdesc_file:UploadFile = File(...),
                        fileparser: FileParser=Depends(get_file_parser),
                        kwextractor: MatchKeywordsService = Depends(get_kw_extraction_service),
                        agent:ResumeAnalyzerAgent= Depends(get_agent_analyzer)):
    """Extract skills from resume and match with job description"""
    try:
        # Save uploaded file temporarily
        resume_file_path = await create_temp_file(resume_file)

        # Save uploaded file temporarily
        jobdesc_file_path = await create_temp_file(jobdesc_file) 
    except Exception as e:
        return {"error.main.getting file path: ": str(e)}
    result = {"Status" : "Started",
                  "feedback":"None",
                  "suggestions": "None",
                  "gaps": "None",
                  "weaknesses": "None",
                  "recomendation": "None",
                  "resume_text": "",
                  "job_description": "",
                  "model_used": LLM_MODEL_TYPE,
                  "scores": {},
                  "dbsaved_ids" : {"resume_id": 1,
                            "jobdesc_id": 1,
                            "matched_results_id":1},}
    try:
        # The Resume and Job Description is now extracted
        resume_text = fileparser.get_raw_text(resume_file_path)         
        job_description = fileparser.get_raw_text(jobdesc_file_path)

        # get the keywords from resume and job description and geta similarity score
        scores = {}
        result["resume_text"]= resume_text
        result["job_description"]= job_description
        result["scores"] = scores
        result = {"Status" : "Started",
                  "feedback":"None",
                  "suggestions": "None",
                  "gaps": "None",
                  "weaknesses": "None",
                  "recomendation": "None",
                  "resume_text": resume_text,
                  "job_description": job_description,
                  "model_used": LLM_MODEL_TYPE,
                  "scores": scores,
                  "dbsaved_ids" : {"resume_id": 1,
                            "jobdesc_id": 1,
                            "matched_results_id":1},}
        kwscores = kwextractor.match_skills(resume_text, job_description) 
        candidate_email = ""
        try:
            sections = kwextractor.get_resume_sections()            
            if isinstance(sections, dict) and "email" in sections:
                candidate_email = sections.get("email", "").strip()
            if candidate_email == "":
                candidate_email = None
        except Exception as e:
            #####print(f"error.main.getting email from resume: {str(e)}")
            candidate_email = None

        scores['similarity_score'] = kwscores.get('similarity_score', 0.0)
        scores['exact_match'] = kwscores.get('exact_match', 0.0)
        scores['overall_score'] = 0.0

        # # Perform Anaysis using an LLM Agent
        agent_result = await agent.analyze_resume(resume_text, job_description, candidate_email)

        #####print(f"agent_result: {agent_result}")

        # # Check for results and format and send it back to frontend
        try:
            llm_analysis_result = agent_result.get("result", {"error": "No result from LLM analysis"})
            result["Error"] =llm_analysis_result.get("error","errorLLM errors not found")
        except Exception as e:
            print(f"\n{'#'*50}\n")
            print(f"llm_analysis_result.feedback/suggestions/rec: \n error: {e}")
        try:
            scores['overall_score'] = llm_analysis_result.get("overall_score", 0) 
        except Exception as e:
            print(f"\n{'#'*50}\n")
            print(f"llm_analysis_result.overall_score : \n error: {e}")
        try:
            result["feedback"] = llm_analysis_result.get("feedback", "") 
            result["suggestions"] = llm_analysis_result.get("suggestions", "") 
            result["recomendation"] = llm_analysis_result.get("recomendation","") 
        except Exception as e:
            print(f"\n{'#'*50}\n")
            print(f"llm_analysis_result.feedback/suggestions/rec: \n error: {e}")
        try:
            result["gaps"] = llm_analysis_result.get("gaps",[]) 
            result["weaknesses"] = llm_analysis_result.get("weaknesses",[]) 
            result["strength"] = llm_analysis_result.get("strength", None) 
        except Exception as e:
            print(f"\n{'#'*50}\n")
            print(f"llm_analysis_result.strength/weaknesses/gaps: \n error: {e}")
        try:
            result["scores"] = scores
        except Exception as e:
            print(f"{'#'*50}")
            print(f"scores: \n error: {e}")
        try:
            result["llm_parsed_resume"] = llm_analysis_result.get("response",{}).get("llm_parsed_resume")
            result["llm_parsed_jd"] = llm_analysis_result.get("response",{}).get("llm_parsed_jd")  
        except Exception as e:
            print(f"{'#'*50}")
            print(f"llm_analysis_result.getresponse: \n {llm_analysis_result.get('response')} \n error: {e}")
        return result
    except Exception as e:
        print(f"error.main.getting file text: {str(e)}")
        # result["Error"] = result.get("Error",[]).append(f"error.main.getting file text: {str(e)}" ) 
        return result
         
    
    finally: 
        # Clean up temp file
        if os.path.exists(resume_file_path):
            os.remove(resume_file_path)
        if os.path.exists(jobdesc_file_path):
            os.remove(jobdesc_file_path)

@app.post("/get-resumes/")
async def get_resumes(payload:DataModel = {}):
    """Get all resumes from the database"""
    # Placeholder for actual database retrieval logic
    # In a real application, you would query your database to get the resumes
    # For demonstration, we'll return a static list of resumes
    try:
        result = {"resumes": [ ]}
        resume_service = ResumeDataService()
        records = resume_service.get_resumes(payload.filters)
        documents = json.loads(json_util.dumps(list(records)))
        if documents is not None: 
            if not isinstance(documents, list): 
                #####print(f"records not list: type: {type(documents)}")
                documents =list(documents) 
                 
            result = {"resumes": documents }  
        # #####print( result)
        return result
    except Exception as e:
        #####print(f"error.main.get_resumes resumes: {str(e)}")
        return {"resumes": [] } 

@app.post("/get-jobs/")
async def get_jobs(payload:DataModel = {},):
    """Get all jobs from the database""" 
    try: 
        result = {"jobs": []}
        job_service = JobDataService()
        records = job_service.get_jobs(payload.filters) 
        documents = json.loads(json_util.dumps(list(records)))
        if documents is not None: 
            if not isinstance(documents, list): 
                #####print(f"records not list: type: {type(documents)}")
                documents =list(documents) 
                 
            result = {"jobs": documents }  
        #####print( result)
        return result 
    except Exception as e:
        #####print(f"error.main.get_jobs :{str(e)}")
        return {} 
    
@app.post("/get-past-matches/")
async def get_past_matches(payload:DataModel = {},):
    """Get all past matches from the database"""
    try: 
        result = {"matches": []}
        resume_job_match_service = ResumeJobMatchDataService()
        records = resume_job_match_service.get_past_matches(payload.filters)
        if records is not None:
            documents = json.loads(json_util.dumps(list(records)))
            if documents is not None: 
                if not isinstance(documents, list): 
                    #####print(f"records not list: type: {type(documents)}")
                    documents =list(documents)                  
                result = {"matches": documents }
        return result
    except Exception as e:
        #####print(f"error.main.get_past_matches :{str(e)}")
        return {}
    #ResumeJobMatchDataService
    

@app.post("/search-candidates-job/")
async def get_candidates_by_job(jobdesc_file:UploadFile = File(...),
                            fileparser: FileParser=Depends(get_file_parser),
                            candfind_agent: CandidateFinderAgent = Depends(get_candidate_finder_agent)):
    """Get best candidates by providing job description
    This is RAG functionality""" 
    result = {"Status" : "Started",
              "candidates": [],
              "errors": [],
              "job_description": "",
        }
    try:
        try:
            # Save uploaded file temporarily
            jobdesc_file_path = await create_temp_file(jobdesc_file) 
        except Exception as e:
            print(f"error.get_candidates_by_job.getting file path: {str(e)}")
            return result
              
        job_description = fileparser.get_raw_text(jobdesc_file_path)
        result["job_description"]= job_description

        # call the agent to get the best candidates
        candidates = await candfind_agent.find_candidates(job_description)
        result["candidates"] = candidates
        result["Status"] = "Completed"
        result["errors"] = candidates.get("errors", [])
        
        return result

    except Exception as e:
        print(f"error.get_candidates_by_job : {str(e)}") 
        return result
    finally:
        # Clean up temp file
        if os.path.exists(jobdesc_file_path):
            os.remove(jobdesc_file_path)
     

@app.post("/search-jobs-resume/")
async def get_jobs_by_resume(resume_file:UploadFile = File(...),
                            fileparser: FileParser=Depends(get_file_parser),
                            jobfind_agent: JobFinderAgent = Depends(get_job_finder_agent)):
    """Get best jobs by providing resume
    This is RAG functionality""" 
    result = {"Status" : "Started",
              "jobs": [],
              "errors": [],
              "resume_text": "",
        }
    try:
        try:
            # Save uploaded file temporarily
            resume_file_path = await create_temp_file(resume_file)
        except Exception as e:
            print(f"error.get_jobs_by_resume.getting file path: {str(e)}")
            return result
              
        resume_text = fileparser.get_raw_text(resume_file_path)
        result["resume_text"]= resume_text

        # call the agent to get the best candidates
        jobs = await jobfind_agent.find_jobs(resume_text)
        result["jobs"] = jobs
        result["Status"] = "Completed"
        result["errors"] = jobs.get("errors", [])
        
        return result

    except Exception as e:
        print(f"error.get_jobs_by_resume : {str(e)}") 
        return result
    finally:
        # Clean up temp file
        if os.path.exists(resume_file_path):
            os.remove(resume_file_path)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


### Run the follwing: uvicorn main:app --reload
# uvicorn main:app --host 0.0.0.0 --port 8000