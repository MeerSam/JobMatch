
from langchain.agents import  initialize_agent, Tool, AgentType
from db.db_connector import get_database
from db.dboperations import MongoDBOperationHandler
from services.analyzer_tools import ExtractResumeTool, ExtractJobDescTool, AnalyzeResumeJobTool  

class ResumeAnalyzerAgent:
    def __init__(self, llm, verbose=False):
        self.llm = llm
        self.err = [] # record any errors that are not critical 
        
        try:
            parser =  ExtractResumeTool(llm)
        except Exception as e:
            parser = None 
            #####print(e)
        self.parse_resume_tool =  ExtractResumeTool(llm)
        self.parse_jobdesc_tool = ExtractJobDescTool(llm)
        self.analyze_resume_tool = AnalyzeResumeJobTool(llm)
        self.verbose = verbose
        self.agentexecutor = initialize_agent( 
            tools=[self.parse_resume_tool, self.parse_jobdesc_tool, self.analyze_resume_tool],
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        ) 
    
    def analyzer(self, resume_data, job_description):
        """ Main entry point for resume analysis. 
        Analyze the resume data against the job description using the llm"""
        try:
            task  =  f"""You are a professional resume analyzer. Analyze this Resume:{resume_data} 
            against this Job description: {job_description}.
            Follow these steps:
            1. Parse the Resume and extract structured information
            2. Save the extracted resume to Mongo Database and return the inserted id
            3. Parse Job description and extract structured information 
            4. Save the extracted Job description to Mongo Database and return the inserted id
            5. Compare the resume against the job requirements. Provide match scores and detailed feedback
            Make sure to use the appropriate tools for each step.
            """ 
            response = self.agentexecutor.run(task)
            if "error" in response:
                raise Exception(f"analyze_resume: Error while parsing resume :- {response['error']}")
            if isinstance(response) == dict:
                return {"result": response,
                        "response" :response,
                        "error": self.err}
        except Exception as e:
            #####print(e)
            self.err.append(f"ResumeAnalyzerAgent.analyze_resume.main: {e}")
            return {"result": None,
                     "response" :{},
                     "error": self.err}
        
    
    

    async def analyze_resume(self, resume_data, job_description, resume_email=None, job_external_id=None):
        """ Main entry point for resume analysis. 
        Analyze the resume data against the job description using the llm"""
        try:
            resume_response ={}
            jobdesc_response = {}
            final_response ={}
            db = get_database()
            ret_resume_id = None
            ret_job_id = None
            # Prior to running the analysis, check if the resume and job description are already done 
            resume_exists = False
            job_exists = False
            match_exists = False 
            if resume_email is not None  :
                filter = {"email": resume_email}
                collection_name = "resume"
                resume_exists, resume_record = self.check_records(db, collection_name, filter, {})      
                if resume_exists:
                    ret_resume_id = resume_record.get("_id")
                    resume_data['resume_id'] = ret_resume_id
                    resume_response ={"response":  resume_record.get("resume_response",None),
                                        "data" : resume_record} 
                     
                    if self.verbose:
                        #####print(f"resume_response: Resume parsing response: {resume_response}")
                        pass
                    else:
                        self.err.append(f"Resume ({resume_email}):  resume not found in database")    
                else:
                    self.err.append(f"Resume ({resume_email}):  resume not found in database")
            if job_external_id is not None:
                filter = {"external_job_id": job_external_id}
                collection_name = "job"
                job_exists, job_record = self.check_records(db, collection_name, filter, {})
                if job_exists:
                    ret_job_id = job_record.get("_id")
                    job_record['job_id'] = ret_job_id
                    jobdesc_response = {"response":  job_record.get("job_response",None),
                                        "data" : job_record}   
                    if self.verbose:
                        #####print(f"jobdesc_response: job description parsing response: {jobdesc_response}")
                        pass
                    else:
                        self.err.append(f"Job Description ({job_external_id}):  Job description not found in database")    
                else:
                    self.err.append(f"Job Description ({job_external_id}):  Job description not found in database")
            # Step 1: Parse the resume 
            if not resume_exists and ret_resume_id is None:
                try:
                    resume_response = await self.parse_resume_tool.arun({"resume_data": resume_data})
                    if self.verbose :
                        #####print(f"resume_response: Resume parsing response: {resume_response}")
                        pass
                    if "error" in resume_response:
                        raise Exception(f"analyze_resume: Error while parsing resume :- {resume_response['error']}")
                except Exception as e:
                    #####print(f"ResumeAnalyzerAgent.resume_response.main: {e}")
                    self.err.append(f"ResumeAnalyzerAgent.resume_response.main: {e}")
            # Step 2: Parse the job description 

            if not job_exists and ret_job_id is None:                
                try:
                    jobdesc_response = await self.parse_jobdesc_tool.arun({"job_description": job_description})
                    if "error" in resume_response:
                        raise Exception(f"analyze_resume: Error while parsing resume :- {jobdesc_response['error']}")
                    if self.verbose :
                        #####print(f"jobdesc_response: job description parsing response: {jobdesc_response}")
                        pass
                except Exception as e:
                    #####print(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
                    pass
                    self.err.append(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
            # Step 3: Parse the job description 
            #####print(f"ret_resume_id: {ret_resume_id} ret_job_id: {ret_job_id}")
            #####print("Starting match check")
            try:
                if ret_resume_id is None  and "resume_id" in resume_response.get("data",{}):
                    ret_resume_id = resume_response.get("data").get("resume_id")
                if ret_job_id is None and "job_id" in jobdesc_response.get("data",{}):
                    ret_job_id = jobdesc_response.get("data").get("job_id")

                if ret_resume_id is None or ret_job_id is None:
                    print(f"Resume ({ret_resume_id})/ Job Description  ({ret_job_id}): Database save error")
                    #####print(f"Resume ({ret_resume_id})/ Job Description  ({ret_job_id}): Database save error")
                try: 
                    filter = {"job_id": ret_job_id, "resume_id": ret_resume_id}
                    collection_name = "jobmatch_result"
                    match_exists, record = self.check_records(db, collection_name, filter, {})
                    if match_exists and record is not None:
                        record['match_id'] = record.get("_id")

                        final_response = {"response" : record.get("match_response",{}),
                                          "data" : record.get("data",{})}
                        if self.verbose:
                            print(f"match_exists: {match_exists} record: {record}")
                        else:
                            self.err.append(f"Match ({ret_resume_id})/ Job Description  ({ret_job_id}): Match not found in database")
                    if match_exists :
                        try:                            
                            final_result = {"response" : {"analysis_response": record.get("match_response",""),
                                                  "resume_response_data" :resume_response.get("data"),
                                                  "jobdesc_response_data" :jobdesc_response.get("data"),
                                                  "analysis_response_data" :record,
                                                  "llm_parsed_resume" : resume_response.get("response",resume_response.get("data").get("resume_response","")),
                                                  "llm_parsed_jd" : jobdesc_response.get("response", jobdesc_response.get("data").get("job_response",""))},
                                    "result": {"overall_score" : record.get("overall_score"),
                                               "feedback" : record.get("feedback"),
                                               "suggestions" : record.get("suggestions"),
                                               "gaps" : record.get("gaps"),
                                               "weaknesses" : record.get("weaknesses"),
                                               "strength" : record.get("strength"),
                                               "recomendation" : record.get("recomendation")
                                               },
                                    "error": self.err}
                            return final_result
                        except Exception as e:
                            self.err.append(f"ResumeAnalyzerAgent.analyze_resume - match results: {e}")


                except Exception as e:
                    self.err.append(f"ResumeAnalyzerAgent.analyze_resume - match results main: {e}")
                # Run the analysis if match does not exist
                print(f"ret_resume_id: {ret_resume_id} | ret_job_id: {ret_job_id}")
                # going to run analysis if match does not exist
                print(f"Running analysis")
                final_response = await self.analyze_resume_tool.arun({"resume_data": resume_data,
                                                                    "job_description": job_description,
                                                                    "resume_id": ret_resume_id,
                                                                    "job_id" : ret_job_id })
                
                print("completing analysis")
                if "data" in final_response :
                    #####print(f'overall_score: {final_response.get("data").get("overall_score")}') 
                    {"overall_score" : final_response.get("data").get("overall_score")}

                    final_result = {"response" : {"analysis_response": final_response.get("response", final_response.get("match_response", "No Final Response from LLM") ),
                                                  "resume_response_data" :resume_response.get("data",{}),
                                                  "jobdesc_response_data" :jobdesc_response.get("data",{}),
                                                  "analysis_response_data" :final_response.get("data",{}),
                                                  "llm_parsed_resume" : resume_response.get("response",resume_response.get("data").get("resume_response","No resume response from LLM")),
                                                  "llm_parsed_jd" : jobdesc_response.get("response", jobdesc_response.get("data").get("job_response","No jobdesc response from LLM"))},
                                    "result": {"overall_score" : final_response.get("data",{}).get("overall_score"),
                                               "feedback" : final_response.get("data",{}).get("feedback"),
                                               "suggestions" : final_response.get("data",{}).get("suggestions"),
                                               "gaps" : final_response.get("data",{}).get("gaps"),
                                               "weaknesses" : final_response.get("data",{}).get("weaknesses"),
                                               "strength" : final_response.get("data",{}).get("strength"),
                                               "recomendation" : final_response.get("data",{}).get("recomendation")
                                               },
                                    "error": self.err}
                    return final_result
                if "error" in final_response:
                    raise Exception(f"analyze_resume: Error while parsing resume :- {final_response['error']}")
                
            except Exception as e:
                #####print(f"ResumeAnalyzerAgent.analyze_resume final..main step: {e}")
                self.err.append(f"ResumeAnalyzerAgent.analyze_resume final.main step: {e}")
            
            return {"response" : {"analysis_response": final_response,
                                  "resume_response" :resume_response.get("data"),
                                  "jobdesc_response" :jobdesc_response.get("data")},
                    "result": final_response,
                    "error": self.err}
            
        except Exception as e:
            self.err.append(f"ResumeAnalyzerAgent.analyze_resume.main: {e}")
            return {"result": None,
                    "error": self.err}

    # sync_analyze_resume is a sync version of the async analyze_resume method.
    # It is used for testing purposes to run the analysis in a synchronous manner.
    # This is useful when you want to test the functionality without using async/await.
    # It is not recommended for production use as it may block the event loop.
    def sync_analyze_resume(self, resume_data, job_description, resume_email=None, job_external_id=None):
        """    Main entry point for resume analysis.
        Analyze the resume data against the job description using the llm"""
        try:
            resume_response ={}
            jobdesc_response = {}
            final_response ={}  
            db = get_database()
            ret_resume_id = None
            ret_job_id = None
            # Prior to running the analysis, check if the resume and job description are already done
            resume_exists = False
            job_exists = False
            match_exists = False 
            if resume_email is not None  :
                try:
                    filter = {"email": resume_email}
                    collection_name = "resume"
                    resume_exists, resume_record = self.check_records(db, collection_name, filter, {})
                    if resume_exists:
                        ret_resume_id = resume_record.get("_id")
                        resume_record['resume_id'] = ret_resume_id
                        resume_response = {"response": resume_record.get("resume_response",None),
                                           "data" : resume_record}
                        if self.verbose:
                            #####print(f"resume_response: Resume parsing response: {resume_response}")
                            pass
                        else:
                            self.err.append(f"Resume ({resume_email}):  resume not found in database")    
                    else:
                        self.err.append(f"Resume ({resume_email}):  resume not found in database")
                except Exception as e:
                    #####print(f"ResumeAnalyzerAgent.resume_response.main: {e}")
                    self.err.append(f"ResumeAnalyzerAgent.resume_response.main: {e}")

            if job_external_id is not None:
                try:
                    filter = {"external_job_id": job_external_id}
                    collection_name = "job"
                    job_exists, job_record = self.check_records(db, collection_name, filter, {})
                    if job_exists:
                        ret_job_id = job_record.get("_id") 
                        job_record['job_id'] = ret_job_id
                        jobdesc_response = {"response":  job_record.get("job_response",None),
                                        "data" : job_record}
                        if self.verbose:
                            #####print(f"jobdesc_response: job description parsing response: {jobdesc_response}")
                            pass
                        else:
                            self.err.append(f"Job Description ({job_external_id}):  Job description not found in database")    
                    else:
                        self.err.append(f"Job Description ({job_external_id}):  Job description not found in database")
                except Exception as e:
                    #####print(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
                    self.err.append(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
            
            if not resume_exists or ret_resume_id is None:
                try:
                    resume_response = self.parse_resume_tool.run({"resume_data": resume_data})
                    if self.verbose :
                        #####print(f"resume_response: Resume parsing response: {resume_response}")
                        pass
                    if "error" in resume_response:
                        raise Exception(f"analyze_resume: Error while parsing resume :- {resume_response['error']}")
                except Exception as e:
                    #####print(f"ResumeAnalyzerAgent.resume_response.main: {e}")
                    self.err.append(f"ResumeAnalyzerAgent.resume_response.main: {e}")
            # Step 2: Parse the job description
            if not job_exists or ret_job_id is None:
                try:
                    jobdesc_response = self.parse_jobdesc_tool.run({"job_description": job_description})
                    if "error" in resume_response:
                        raise Exception(f"analyze_resume: Error while parsing resume :- {jobdesc_response['error']}")
                    if self.verbose :
                        #####print(f"jobdesc_response: job description parsing response: {jobdesc_response}")
                        pass
                except Exception as e:
                    #####print(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
                    self.err.append(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
            # Step 3: Parse the job description
            # Check match exists in the database
            if ret_resume_id is not None and ret_job_id is not None:
                try:
                    filter = {"job_id": ret_job_id, "resume_id": ret_resume_id}
                    collection_name = "jobmatch_result"
                    match_exists, record = self.check_records(db, collection_name, filter, {})
                    if match_exists :
                        try:
                            record['match_id'] = record.get("_id")
                            final_response = {"response": record.get("match_response",None),
                                           "data" : record}
                            final_result = {"response" : {"analysis_response": record.get("match_response",""),
                                                "resume_response_data" :resume_response.get("data",{}),
                                                "jobdesc_response_data" :jobdesc_response.get("data",{}),
                                                "analysis_response_data" :record,
                                                "llm_parsed_resume" : resume_response.get("response",resume_response.get("data").get("resume_response","")),
                                                "llm_parsed_jd" : jobdesc_response.get("response", jobdesc_response.get("data").get("job_response",""))},
                                            "result":{"overall_score" : record.get("overall_score",""),
                                                "feedback" : record.get("feedback",""),
                                                "suggestions" : record.get("suggestions",""),
                                                "gaps" : record.get("gaps"),
                                                "weaknesses" : record.get("weaknesses",""),
                                                "strength" : record.get("strength",""),
                                                "recomendation" : record.get("recomendation","")},
                                            "error": self.err}
                            return final_result
                        except Exception as e:
                            print(f"ResumeAnalyzerAgent.sync_analyze_resume - match results: {e}")
                except Exception as e:
                    print(f"ResumeAnalyzerAgent.sync_analyze_resume - match results main: {e}")
             
            # Run the analysis if match does not exist
            if not match_exists :
                try:
                    ret_resume_id = resume_response.get("data").get("resume_id") if ret_resume_id is None else ret_resume_id
                    if ret_resume_id is None and "data" in resume_response:
                        ret_resume_id = resume_response.get("data").get("_id")
                        self.err.append(f"Resume ({ret_resume_id}): Database save error")
                    
                    ret_job_id = jobdesc_response.get("data").get("job_id") if ret_job_id is None else ret_job_id
                    if ret_job_id is None and "data" in resume_response:
                        ret_job_id = jobdesc_response.get("data").get("_id")
                    if ret_resume_id is None or ret_job_id is None:
                        self.err.append(f"Resume ({ret_resume_id})/ Job Description  ({ret_job_id}): Database save error")
                    
                    final_response = self.analyze_resume_tool.run({"resume_data": resume_data,
                                                                        "job_description": job_description,
                                                                        "resume_id": ret_resume_id,
                                                                        "job_id" : ret_job_id })
                    
                    if "data" in final_response :
                        #####print(f'overall_score: {final_response.get("data").get("overall_score")}') 
                        {"overall_score" : final_response.get("data").get("overall_score")}

                        final_result = {"response" : {"analysis_response": final_response.get("response"),
                                                    "resume_response_data" :resume_response.get("data"),
                                                    "jobdesc_response_data" :jobdesc_response.get("data"),
                                                    "llm_parsed_resume" : resume_response.get("response"),
                                                    "llm_parsed_jd" : jobdesc_response.get("response")},
                                        "result": {"overall_score" : final_response.get("data").get("overall_score"),
                                                "feedback" : final_response.get("data").get("feedback"),
                                                "suggestions" : final_response.get("data").get("suggestions"),
                                                "gaps" : final_response.get("data").get("gaps"),
                                                "weaknesses" : final_response.get("data").get("weaknesses"),
                                                "strength" : final_response.get("data").get("strength"),
                                                "recomendation" : final_response.get("data").get("recomendation")
                                                },
                                        "error": self.err}
                        return final_result
                    if "error" in resume_response:
                        raise Exception(f"analyze_resume: Error while parsing resume :- {final_response['error']}")

                except Exception as e:
                    #####print(f"ResumeAnalyzerAgent.analyze_resume final.main: {e}")
                    self.err.append(f"ResumeAnalyzerAgent.analyze_resume final.main: {e}")
            
            return {"result": final_response.get("data",{}),
                    "response" :{"analysis_response": final_response.get("response"),
                                                    "resume_response_data" :resume_response.get("data"),
                                                    "jobdesc_response_data" :jobdesc_response.get("data"),
                                                    "llm_parsed_resume" : resume_response.get("response"),
                                                    "llm_parsed_jd" : jobdesc_response.get("response")},
                    "error": self.err}
        except Exception as e:
            #####print(f"ResumeAnalyzerAgent.analyze_resume.main: {e}")
            self.err.append(f"ResumeAnalyzerAgent.analyze_resume.main: {e}") 
            return {"result": None,
                     "response" :{},
                     "error": self.err}
    # Sync Version for Testing   
    def sync_analyze_resume_old(self, resume_data, job_description):
        """ Main entry point for resume analysis. 
        Analyze the resume data against the job description using the llm"""
        try:
            resume_response ={}
            jobdesc_response = {}
            final_response ={}            
            db = get_database()
            # Step 1: Parse the resume 
            try:
                resume_response = self.parse_resume_tool.run({"resume_data": resume_data})
                if self.verbose :
                    #####print(f"resume_response: Resume parsing response: {resume_response}")
                    pass
                if "error" in resume_response:
                    raise Exception(f"analyze_resume: Error while parsing resume :- {resume_response['error']}")
            except Exception as e:
                #####print(f"ResumeAnalyzerAgent.resume_response.main: {e}")
                self.err.append(f"ResumeAnalyzerAgent.resume_response.main: {e}")
            # Step 2: Parse the job description 
            try:
                jobdesc_response = self.parse_jobdesc_tool.run({"job_description": job_description})
                if "error" in resume_response:
                    raise Exception(f"analyze_resume: Error while parsing resume :- {jobdesc_response['error']}")
                if self.verbose :
                    #####print(f"jobdesc_response: job description parsing response: {jobdesc_response}")
                    pass
            except Exception as e:
                print(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
                self.err.append(f"ResumeAnalyzerAgent.jobdesc_response.main: {e}")
            # Step 3: Parse the job description 
            try:
                ret_resume_id = resume_response.get("data").get("resume_id")
                ret_job_id = jobdesc_response.get("data").get("job_id")
                if ret_resume_id is None or ret_job_id is None:
                    self.err.append(f"Resume ({ret_resume_id})/ Job Description  ({ret_job_id}): Database save error")
                final_response = self.analyze_resume_tool.run({"resume_data": resume_data,
                                                                    "job_description": job_description,
                                                                    "resume_id": ret_resume_id,
                                                                    "job_id" : ret_job_id })
                
                if "data" in final_response :
                    #####print(f'overall_score: {final_response.get("data").get("overall_score")}') 
                    {"overall_score" : final_response.get("data").get("overall_score")}

                    final_result = {"response" : {"analysis_response": final_response.get("response"),
                                                  "resume_response_data" :resume_response.get("data"),
                                                  "jobdesc_response_data" :jobdesc_response.get("data"),
                                                  "llm_parsed_resume" : resume_response.get("response"),
                                                  "llm_parsed_jd" : jobdesc_response.get("response")},
                                    "result": {"overall_score" : final_response.get("data").get("overall_score"),
                                               "feedback" : final_response.get("data").get("feedback"),
                                               "suggestions" : final_response.get("data").get("suggestions"),
                                               "gaps" : final_response.get("data").get("gaps"),
                                               "weaknesses" : final_response.get("data").get("weaknesses"),
                                               "strength" : final_response.get("data").get("strength"),
                                               "recomendation" : final_response.get("data").get("recomendation")
                                               },
                                    "error": self.err}
                    return final_result
                if "error" in resume_response:
                    raise Exception(f"analyze_resume: Error while parsing resume :- {final_response['error']}")

            except Exception as e:
                #####print(f"ResumeAnalyzerAgent.analyze_resume final.main: {e}")
                self.err.append(f"ResumeAnalyzerAgent.analyze_resume final.main: {e}")
            return {"result": final_response,
                    "error": self.err}
            
        except Exception as e:
            self.err.append(f"ResumeAnalyzerAgent.analyze_resume.main: {e}")
            return {"result": None,
                    "error": self.err}


    def check_records(self, db,collection_name, filter, projection:dict={}):  
                            
        if db is not None:
            objdbservice = MongoDBOperationHandler(db)
            record = objdbservice.get_record(collection_name, filter, projection )
            if record is not None and record['_id']:
                # self.match_id = record['_id']
                match_exists = True
        return  match_exists, record