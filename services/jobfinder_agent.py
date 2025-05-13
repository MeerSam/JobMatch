
import os


class JobFinderAgent:
    def __init__(self, llm, db):
        self.llm = llm
        self.err =[]
        db = db

    def find_jobs(self, resume_data):
        """ The agent will find the best jobs for the given resume data. """
        # Use the LLM to find the best jobs for the given resume data
        matched_jobs = [] 
        return matched_jobs 
    
    def fetch_jobs(self):
        """Fetch jobs from MongoDB"""
        # Connect to MongoDB and fetch jobs
        # This is a placeholder for the actual MongoDB connection and fetching logic
        jobs = []
        jobs_db_Name = os.environ.get("JOBSLIST", "jobs_list")
        collection = self.db[jobs_db_Name]
        jobs  = list(self.collection.find())
        return jobs
    
    def rank_jobs(self, resume_info, jobs):
        """Rank jobs based on the resume information"""
        # This is a placeholder for the actual ranking logic
        ranked_jobs = []
        for job in jobs:
            score = self.calculate_job_score(resume_info, job)
            ranked_jobs.append((job, score))
        
        # Sort jobs by score
        ranked_jobs.sort(key=lambda x: x[1], reverse=True)
        return ranked_jobs
    
    def get_top_matching_jobs(self, resume_file, top_n=5):
        """Get the top matching jobs for a given resume"""
        # Extract text from resume
        resume_text = self.extract_text_from_resume(resume_file)
        
        # Preprocess text
        processed_text = self.preprocess_text(resume_text)
        
        # Extract resume information
        resume_info = self.extract_resume_info(processed_text)
        
        # Fetch jobs from MongoDB
        jobs = self.fetch_jobs()
        
        # Rank jobs
        ranked_jobs = self.rank_jobs(resume_info, jobs)
        
        # Get top N jobs
        top_jobs = ranked_jobs[:top_n]