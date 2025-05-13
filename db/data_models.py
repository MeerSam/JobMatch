import json
from pydantic import BaseModel, Field
from typing import List, Dict,Any, Optional

class DataModel(BaseModel):
    filters: Dict  # Accepts a dictionary
class ResumeResponseModel(BaseModel):
    """Use for model parsing the response: resume parsing using llm response to save to Database"""
    name: str = Field(description="Name of the candidate from resume")
    email: str
    phone: str     
    summary : str
    skills: Dict[str, List[str]]
    work_history: List[Dict]
    education: List[Dict]
    certifications: List[str]
    professional_experience: Dict[str, Any] 
 
class JobResponseModel(BaseModel):
    """Use for model parsing the response: job description parsing using llm response to save to Database"""
    external_job_id: Optional[str]
    job_title: str
    company_name: Optional[str] 
    required_experience : Optional[List[str]]= None
    key_responsibilities: Optional[List[str]]= None
    qualifications: Optional[List[str]] = None
    required_skills: Optional[Dict[str,List[str]]] = None
    must_haves: Optional[List[str]] = None
    nice_to_haves:Optional[List[str]] = None
    importance_scores: Optional[Dict] = None

class AnalysisResponseModel(BaseModel):
    """ structured results from the Evaluation agent"""
    name: str = Field(description="Name of the candidate from resume")
    email: str = Field(description="Name of the candidate from resume")
    external_job_id: str = Field(description="if a unique job id, url to job or identifier was mentioned.")
    overall_score :int  = Field(description="Overall match score from 0-100")
    feedback : str = Field(description="Feedback on why the candidate is a good match or not ") 
    suggestions : str =Field(description="suggestion to candidates for this role")
    recomendation: str= Field(description="Recommendations for the candidate")
    gaps: List[str]= Field(description="List of missing skills or qualifications")
    weaknesses : List[str]= Field(description="weakness of the candidate resume against job description")
    strengths: List[str] = Field(description="List of candidate strengths for this role")
    
     
# class AnalysisUserResultModel(BaseModel):
#     """ Use for returning a structured results back to the User"""
#     resume_id: int  = Field(description="Id of the Resume in MongoDb")
#     job_id: int  = Field(description="Id of the job description in MongoDb")
#     overall_score :int  = Field(description="Overall match score from 0-100")
#     kw_match_score : int = Field(description="skills extact match score from 0-100") 
#     semantic_match_score : int =Field(description="semantic match score from 0-100")
#     suggestions : List[str] =Field(description="List of candidate strengths for this role")
#     strength: List[str] =Field(description="List of candidate strengths for this role")
#     gaps: List[str]= Field(description="List of missing skills or qualifications")
#     recomendation: List[str]= Field(description="Recommendations for the candidate")


# class MatchDocumentsDBModel(BaseModel):
#     """ Use for Model the Match Results from Analysis to save to Database"""
#     resume_id: int
#     job_id: int 
#     raw_resume : str
#     raw_jobdesc : str     
#     resume_json : dict
#     llm_resume_json: dict
#     llm_jd_json: dict
#     strengths: List[str]
#     feedback: List[str]
#     skill_gap : List[str]
#     suggestions: List[str]

# class ResumeDBModel(BaseModel):
#     """ Use for Model the Match Results from Analysis to save to Database"""
#     name: str
#     email: str
#     phone: str
#     skills : str     
#     summary : str
#     skills: Dict
#     work_history: List[Dict]
#     education: List[Dict]
#     feedback: str
#     professional_experience : Dict
#     suggestions: str
#     resume_json : Dict    
#     raw_resume : str

# class SkillsModel(BaseModel):
#     technical:List[str]
#     softskills:List[str]

# class WorkHistoryModel(BaseModel):
#     company_name = str
#     job_title = str
#     start_date = str
#     end_date = str
#     location = str

# class ProfessionalExpModel(BaseModel):
#     total_years : int
#     domains: List[str]
#     positions:List[str]
#     achievements: List[str]


# class ResumeAnalyzerSystem:
#     def __init__(self, llm,st_embeddings, embedding, nlp_tool, tfidf_tool ):         
#         self.llm = llm
#         self.st_embeddings = st_embeddings
#         self.embedding = embedding
#         self.nlp_tool = nlp_tool
#         self.tfidf = tfidf_tool
#     def generate_full_analysis(self):
#         return {"status" : "Success"}
#     def get_key(key="status"):
#         try:
#             return {"status" : "Success"}
#         except Exception as e:
#             return {"err" : f"error getting key{e}"}