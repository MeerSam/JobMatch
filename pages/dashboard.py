import json
import pandas as pd
import streamlit as st
import requests
import os
from streamlit_extras.colored_header import colored_header
API_URL= os.environ.get('FASTAPI_URL', "http://localhost:8000")
 

st.set_page_config(
    page_title="JobMatch: Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Create tabs for Resumes and Jobs
tab1, tab2, tab3 = st.tabs(["Resumes", "Jobs", "Job-Resume Matcher"])

# Resumes Tab
with tab1:
    try:
        response_resumedata = {}
        st.header("All Resumes") 
        # Call the api to get all resumes
        response = requests.post(f"{API_URL}/get-resumes",json={"filters": {}})

        if response.status_code != 200:
            st.error(f"Error fetching resume: {response.status_code}")
            st.markdown(f"response.status_code: \n{response}")           
        else:
            st.success("resumes fetched successfully!") 
            if not isinstance(response, dict):
                response_resumedata = response.json() 
            else: 
                response_resumedata = response 
            
        if isinstance(response_resumedata, dict) and "resumes" in response_resumedata:
            resumes = response_resumedata.get("resumes", [])
        if isinstance(response_resumedata, dict)  :
            resumes = response_resumedata 

        if not response_resumedata :
            st.info("No resumes added yet.")
            # Display all resumes
            with open(('db/data/resumes.json'), 'r') as f: 
                alldata = json.load(f)
            if isinstance(alldata, dict):
                resumes = alldata.get("resumes", [])
            else:
                resumes = alldata
        else:
            for type_item, values in response_resumedata.items():
                if type_item == "resumes":
                    resumes = values    
            resume_df = pd.DataFrame([
                {
                    "ID": resume.get("_id", {}).get("$oid", "") if isinstance(resume, dict) else "",
                    "Name": resume["name"] if isinstance(resume, dict) and "name" in resume else "",
                    "Email": resume.get("email", "") if isinstance(resume, dict) else "",
                    "Skills": ", ".join(resume.get("skills", [])) if isinstance(resume, dict) else "",
                    "education":"\n".join((item.get("degree","") if isinstance(item, dict) else "") for item in resume.get("education", [])) if isinstance(resume, dict) and "education" in resume else "",
                    "Summary": resume["summary"] if isinstance(resume, dict) and "summary" in resume else "",
                } for resume in resumes if resume  # Skip None values
            ])
            
            st.dataframe(resume_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching resumes: {e}")
        # st.markdown(f"response.status_code: \n{response.status_code if response is not None else 'N/A'}")
            
# Jobs Tab
with tab2:
    try:
        response_jobsdata = {}
        st.header("All Jobs")
        # Display all jobs
        # Call the api to get all jobs
        response = requests.post(f"{API_URL}/get-jobs/",json={"filters": {}})
        if response.status_code != 200:
            st.error(f"Error fetching jobs: {response.status_code}")
            st.markdown(f"response.status_code: \n{response}")           
        else:
            st.success("Jobs fetched successfully!") 
            if not isinstance(response, dict):
                response_jobsdata = response.json() 
            else: 
                response_jobsdata = response 
        if isinstance(response_jobsdata, dict) and "jobs" in response_jobsdata:
            jobs = response_jobsdata.get("jobs", [])
        elif isinstance(response_jobsdata, list)  :
            jobs = response_jobsdata

        if  not isinstance(jobs, list):
            with open(('db/data/resumes.json'), 'r') as f: 
                alldata = json.load(f)
            if isinstance(alldata, dict):
                jobs = alldata.get("jobs", [])
            else:
                jobs = alldata

        #####print(response_jobsdata)
        if isinstance(jobs, dict) and "jobs" in jobs: 
            st.info(f"len(jobs): {len(jobs)}")
            
        if not jobs :
            st.info("No jobs added yet.")
        else: 
            # Create a DataFrame for better display
            job_df = pd.DataFrame([
                {
                    "ID": job.get("_id", {}).get("$oid", "") if isinstance(job, dict) else "",
                    "Job ID": job.get("external_job_id", "") if isinstance(job, dict) and "external_job_id" in job else "",
                    "Title": job["title"] if isinstance(job, dict) and "title" in job else "",
                    "Company": job.get("company", "") if isinstance(job, dict) and "company" in job else "", 
                    "Location": job.get("location", "") if isinstance(job, dict) and "location" in job else "",
                    "Salary": job.get("salary", "") if isinstance(job, dict)and "salary" in job else "",
                    "Skills": ", ".join(job.get("required_skills", {}).get("technical_skills", [])) if isinstance(job, dict) else "",
                } for job in jobs
            ])   
            st.dataframe(job_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
        # st.markdown(f"response.status_code: \n{response.status_code if response is not None else 'N/A'}")
with tab3:
    try:
        response_matchdata = {}
        matches = None
        st.header("Past Match History")
        # Display all jobs
        # Call the api to get all jobs
        response = requests.post(f"{API_URL}/get-past-matches/",json={"filters": {}})
        if response.status_code != 200:
            st.error(f"Error fetching jobs: {response.status_code}")
            st.markdown(f"response.status_code: \n{response}")           
        else:
            st.success("Past Matches fetched successfully!") 
            if not isinstance(response, dict):
                response_matchdata = response.json() 
            else: 
                response_matchdata = response 

        if isinstance(response_matchdata, dict) and "matches" in response_matchdata:
            matches = response_matchdata.get("matches", [])
        elif isinstance(response_matchdata, list)  :
            matches = response_matchdata 
        
        if matches is None :
            st.info("No matches added yet.")
        else:
            # Create a DataFrame for better display             
            match_df = pd.DataFrame([
            {
                "ID": match_hist.get("_id", {}).get("$oid", "") if isinstance(match_hist, dict) else "",
                "Resume Name": match_hist.get("name", {}) if isinstance(match_hist, dict) and "name" in match_hist  else "",
                "external_job_id":match_hist.get("external_job_id", {}) if isinstance(match_hist, dict) and "external_job_id" in match_hist else "",
                "Overall_score": match_hist.get("overall_score", {}) if isinstance(match_hist, dict) else "",
                "Weaknesses": ", ".join(match_hist.get("weaknesses", []))  if isinstance(match_hist, dict) else "", 
                "Gaps": ", ".join(match_hist.get("gaps", []))  if isinstance(match_hist, dict) else "", 
            } for match_hist in matches
            ])   

            st.dataframe(match_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching Resume-Job Match History: {e}")
        # st.markdown(f"response.status_code: \n{response.status_code if response is not None else 'N/A'}")
