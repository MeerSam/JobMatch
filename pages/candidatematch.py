import json
import pandas as pd
import streamlit as st
import requests
import os
from streamlit_extras.colored_header import colored_header
API_URL= os.environ.get('FASTAPI_URL', "http://localhost:8000")

st.set_page_config(
    page_title="CandidateMatch: Best Candidates for your job requirements",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
st.header("Welcome CandidateMatch: Best Candidates by Job Description")
st.subheader("Upload your job description to lookup best candidates for the job")

if "run_rerun" not in st.session_state:
    st.session_state.run_rerun = False
elif "run_rerun" in st.session_state and st.session_state.run_rerun:
    st.session_state.run_rerun = False
    st.rerun()
    
 # Upload JD
st.subheader("Job Description")
st.write("Upload your job description file here. Hit Search 🔍 and your best candidates will be listed below.")
jobdesc_file = st.file_uploader("Choose a job desciption file", type=["pdf", "docx", ".txt"])

st.session_state.candidatematch_file = jobdesc_file 

def start():
    if jobdesc_file is None:
        st.error("Job Description file not provided. Upload Job Description file") 
        return
    else:
        st.success("Job Description uploaded successfully!")
        with st.spinner("Looking for best matching Candidates for this job...Wait for it...", show_time=True):      
            if jobdesc_file:
                files = {"resume_file": (jobdesc_file.name, jobdesc_file.getvalue(), jobdesc_file.type)}
                response = requests.post(f"{API_URL}/search-candidates-job", files=files)
                # Display results (assuming the result is a structured JSON or similar)
                if response.status_code == 200:
                    data = response.json() 
                    try:
                        if isinstance(data, dict):   
                            print(f"datakeys:\n{data.keys()}")
                        else:
                            print(f"response.status_code: \n{response.status_code}")

                    except Exception as e:
                        st.error(f"response.status_code: \n{response.status_code}. exception : {e}")
def clear():
    st.session_state.candidatematch_file = None 
    st.session_state.data = None
    st.session_state.clear()
    st.success("Files and Past data is cleared successfully!")
    st.session_state.run_rerun = True 

if "run_rerun" in st.session_state and st.session_state.run_rerun:
    st.session_state.run_rerun = False
    st.rerun()

st.button("Clear", on_click=clear )

if st.button("Search Candidates 🔍"):
    start()
    st.session_state.candidatematch_file = jobdesc_file