from typing import Annotated, Any, Type,Optional 
from langchain.tools import BaseTool, StructuredTool , Tool
from pydantic import BaseModel, Field, validator
from services.analyzer_chains import AnalyzerChain, JobDescParserChain, ResumeParserChain
from bson.objectid import ObjectId

class ParseResumeInput(BaseModel):
    resume_data: str = Field(..., description="The text of the resume to parse") 
    # This allows the model to handle both string and dictionary inputs
    # @validator('resume_data', pre=True)
    # def extract_text_from_dict(cls, value):
    #     if isinstance(value, dict) and 'description' in value:
    #         return value['description']
    #     return value

class ParseJDInput(BaseModel):
    job_description: str = Field(..., description="The text of the job description to parse")
    # Add other parameters you need
    # format_type: str = Field(default="json", description="Output format type")
    # # etc.

class ParseAnalyzerInput(BaseModel):
    resume_data: str = Field(..., description="The text of the resume to parse and analyze") 
    job_description: str = Field(..., description="The text of the job description to parse and analyze")
    resume_id: Optional[Any] = Field(None, description="Id of the Resume in MongoDb")
    job_id: Optional[Any] = Field(None, description="Id of the job description in MongoDb")


class ExtractResumeTool(StructuredTool):
    name: str = "parse_extract_resume"
    description: str = "Extract resume details and sections"
    args_schema: Type[BaseModel]  = ParseResumeInput 
    llm : Any = None
    resume_parser_chain: Any = None 
    def __init__(self, llm):
        super().__init__() 
        self.resume_parser_chain = ResumeParserChain(llm)
    
    # def _run(self, inputs: dict, config: dict = None, **kwargs) -> dict: 
    #     return self.resume_parser_chain.run(inputs.get("resume_data"))
    
    def _run(self, *args, **kwargs) -> dict: 
        # Handle both ways of passing arguments
        if args and isinstance(args[0], dict):
            inputs = args[0]
        elif 'inputs' in kwargs:
            inputs = kwargs['inputs']
        else:
            # Try to construct inputs from kwargs directly
            inputs = kwargs
        resume_text =inputs.get("resume_data") 
        # Handle dictionary format
        if isinstance(resume_text, dict) and 'description' in resume_text:
            resume_data = resume_text['description']
        else:
            resume_data = resume_text

        return self.resume_parser_chain.run(resume_data)
    
    # Async version
    async def _arun(self, *args, **kwargs) -> dict: 
        # Handle both ways of passing arguments
        if args and isinstance(args[0], dict):
            inputs = args[0]
        elif 'inputs' in kwargs:
            inputs = kwargs['inputs']
        else:
            # Try to construct inputs from kwargs directly
            inputs = kwargs
        resume_text =inputs.get("resume_data") 
        # Handle dictionary format
        if isinstance(resume_text, dict) and 'description' in resume_text:
            resume_data = resume_text['description']
        else:
            resume_data = resume_text

        return await self.resume_parser_chain.arun(resume_data)
    
class ExtractJobDescTool(StructuredTool):
    name: str = "parse_extract_jobdescription"
    description: str = "Extract key deatils from the job description"
    args_schema: Type[BaseModel] = ParseJDInput
    llm : Any = None
    jobdesc_parser_chain: Any = None
    def __init__(self, llm):
        super().__init__()       
        self.llm = llm 
        self.jobdesc_parser_chain = JobDescParserChain(self.llm)
    
    # def _run(self, inputs: dict, config: dict = None, **kwargs) -> dict: 
    #     return self.jobdesc_parser_chain.run(inputs.get("job_description"))
    
    def _run(self, *args, **kwargs) -> dict: 
        # Handle both ways of passing arguments
        if args and isinstance(args[0], dict):
            inputs = args[0]
        elif 'inputs' in kwargs:
            inputs = kwargs['inputs']
        else:
            # Try to construct inputs from kwargs directly
            inputs = kwargs 

        jd_desc_text =inputs.get("job_description")
        # Handle dictionary format
        if isinstance(jd_desc_text, dict) and 'description' in jd_desc_text:
            job_description = jd_desc_text['description']
        else:
            job_description = jd_desc_text
 
        return self.jobdesc_parser_chain.run(job_description)
    
    async def _arun(self, *args, **kwargs) -> dict: 
        # Handle both ways of passing arguments
        if args and isinstance(args[0], dict):
            inputs = args[0]
        elif 'inputs' in kwargs:
            inputs = kwargs['inputs']
        else:
            # Try to construct inputs from kwargs directly
            inputs = kwargs 

        jd_desc_text =inputs.get("job_description")
        # Handle dictionary format
        if isinstance(jd_desc_text, dict) and 'description' in jd_desc_text:
            job_description = jd_desc_text['description']
        else:
            job_description = jd_desc_text
 
        return await self.jobdesc_parser_chain.arun(job_description)
    

class AnalyzeResumeJobTool(StructuredTool):
    name: str = "evaluate_resume_jobdescription"
    description: str = "Analyze and Evaluate the Resume against the Job Description and return score and detailed analysis"
    args_schema: Type[BaseModel] = ParseAnalyzerInput 
    llm : Any = None
    analyzer_chain: Any = None
    resume_id: Any = None
    job_id: Any = None
    def __init__(self, llm): 
        super().__init__()   
        self.llm = llm
        self.analyzer_chain = AnalyzerChain(self.llm)
    
    # def _run(self, inputs: dict, config: dict = None, **kwargs) -> dict: 
    #     self.resume_id =inputs.get("resume_id") 
    #     self.job_id = inputs.get("job_id")
    #     return self.analyzer_chain.run(inputs.get("resume_data"), inputs.get("job_description"), self.resume_id, self.job_id )
    
    def _run(self, *args, **kwargs) -> dict: 
        # Handle both ways of passing arguments
        if args and isinstance(args[0], dict):
            inputs = args[0]
        elif 'inputs' in kwargs:
            inputs = kwargs['inputs']
        else:
            # Try to construct inputs from kwargs directly
            inputs = kwargs
            jd_desc_text =inputs.get("job_description")

        jd_desc_text =inputs.get("job_description")
        # Handle dictionary format
        if isinstance(jd_desc_text, dict) and 'description' in jd_desc_text:
            job_description = jd_desc_text['description']
        else:
            job_description = jd_desc_text

        resume_text =inputs.get("resume_data") 
        # Handle dictionary format
        if isinstance(resume_text, dict) and 'description' in resume_text:
            resume_data = resume_text['description']
        else:
            resume_data = resume_text

        self.resume_id =inputs.get("resume_id") 
        self.job_id = inputs.get("job_id")
        return self.analyzer_chain.run(resume_data, job_description, inputs.get("resume_id"), inputs.get("job_id") )
    
    async def _arun(self, *args, **kwargs) -> dict: 
        # Handle both ways of passing arguments
        if args and isinstance(args[0], dict):
            inputs = args[0]
        elif 'inputs' in kwargs:
            inputs = kwargs['inputs']
        else:
            # Try to construct inputs from kwargs directly
            inputs = kwargs
            jd_desc_text =inputs.get("job_description")

        jd_desc_text =inputs.get("job_description")
        # Handle dictionary format
        if isinstance(jd_desc_text, dict) and 'description' in jd_desc_text:
            job_description = jd_desc_text['description']
        else:
            job_description = jd_desc_text

        resume_text =inputs.get("resume_data") 
        # Handle dictionary format
        if isinstance(resume_text, dict) and 'description' in resume_text:
            resume_data = resume_text['description']
        else:
            resume_data = resume_text

        for key, value in inputs.items():
            print(f"{key}: {value}") 

        self.resume_id =inputs.get("resume_id") 
        self.job_id = inputs.get("job_id")
        return await self.analyzer_chain.arun(resume_data, job_description, inputs.get("resume_id"), inputs.get("job_id") )
    
     