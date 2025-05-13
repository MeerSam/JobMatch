

from db.db_connector import get_database
from db.dboperations import MongoDBOperationHandler


class ResumeDataService:
    def __init__(self):
        self.db = get_database()
        self.err = []

    def get_resume_data(self, resume_id):
        # Fetch resume data from the database using the provided resume_id
        resume_data = self.db.get_resume_by_id(resume_id)
        return resume_data

    def update_resume_data(self, resume_id, updated_data):
        # Update the resume data in the database with the provided updated_data
        self.db.update_resume(resume_id, updated_data)

    def get_resumes(self, filter: dict = {}):
        """Get all resumes from the database"""
        try:            
            collection_name = "resume"
            if self.db is not None:
                objdbservice = MongoDBOperationHandler(self.db)
                projection={} 
                records = objdbservice.get_records(collection_name, filter )   
                if records is not None : 
                    return records
                else:
                    self.err.append(f"ResumeDataService.get_resumes: No records found")
                    return None
        except Exception as e:
            #####print(f"ResumeDataService.get_resumes.main: {e}")
            self.err.append(f"ResumeDataService.get_resumes.main: {e}")
            return None
        

class JobDataService:
    def __init__(self):
        self.db = get_database()
        self.err = []
    def get_job_data(self, job_id):
        # Fetch job data from the database using the provided job_id
        job_data = self.db.get_job_by_id(job_id)
        return job_data

    def update_job_data(self, job_id, updated_data):
        # Update the job data in the database with the provided updated_data
        self.db.update_job(job_id, updated_data)

    def get_jobs(self, filter: str = None):
        """Get all jobs from the database"""
        try:            
            collection_name = "job"
            if self.db is not None:
                objdbservice = MongoDBOperationHandler(self.db)
                records = objdbservice.get_records(collection_name, filter )
                records = objdbservice.get_records(collection_name, filter )   
                if records is not None : 
                    return records
                else:
                    self.err.append(f"JobDataService.get_resumes: No records found")
                    return None
                
        except Exception as e:
            #####print(e)
            self.err.append(f"JobDataService.get_jobs.main: {e}")
            return {"result": None,
                    "error": self.err}
        
class ResumeJobMatchDataService:
    def __init__(self):
        self.db = get_database()
        self.err = []
    def get_resume_job_match_data(self, match_id):
        # Fetch resume-job match data from the database using the provided match_id
        match_data = self.db.get_resume_job_match_by_id(match_id)
        return match_data

    def update_resume_job_match_data(self, match_id, updated_data):
        # Update the resume-job match data in the database with the provided updated_data
        self.db.update_resume_job_match(match_id, updated_data)

    def get_past_matches(self, filter: str = None):
        """Get all resume-job matches from the database"""
        try:            
            collection_name = "jobmatch_result"
            if self.db is not None:
                objdbservice = MongoDBOperationHandler(self.db)
                records = objdbservice.get_records(collection_name, filter )
                if records is not None : 
                    return records
                else:
                    self.err.append(f"JobDataService.get_resumes: No records found")
                    return None
                # if records is not None :
                #     # Convert the cursor to a list of dictionaries
                #     return {"result": list(records),
                #             "error": self.err}
                # else:
                #     self.err.append(f"ResumeJobMatchDataService.get_resume_job_matches: No records found")
                #     return {"result": None,
                #             "error": self.err}
        except Exception as e:
            #####print(e)
            self.err.append(f"ResumeJobMatchDataService.get_resume_job_matches.main: {e}")
            return {"result": None,
                    "error": self.err}