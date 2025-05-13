import json
import pandas as pd
import streamlit as st
import requests
import os
from streamlit_extras.colored_header import colored_header
API_URL= os.environ.get('FASTAPI_URL', "http://localhost:8000")
st.set_page_config(
    page_title="JobMatch: Best Jobs for You",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header("Welcome JobMatch: Best jobs for you")
st.subheader("Upload your resume to lookup best jobs for you")

st.subheader("Resume")
st.write("Upload your resume file here. Hit Search 🔍 and your best jobs will be listed below.")
resume_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])
 
if "run_rerun" not in st.session_state:
    st.session_state.run_rerun = False
elif "run_rerun" in st.session_state and st.session_state.run_rerun:
    st.session_state.run_rerun = False
    st.rerun()
    
def start():
    if resume_file is None:
        st.error("Resume file not provided. Upload Resume") 
        return
    elif resume_file:
        st.success("Resume uploaded successfully!")
        with st.spinner("Looking for best matching jobs for this resume...Wait for it...", show_time=True):      
            if resume_file:
                files = {"resume_file": (resume_file.name, resume_file.getvalue(), resume_file.type)}
                # Call the API to search for jobs
                response = requests.post(f"{API_URL}/search-jobs-resume", files=files)
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
                    st.markdown(response.text)
                else:
                    st.error(f"Failed to fetch data. Status code: No response from server {response.status_code}")
def clear():
    st.session_state.jobmatch_resume_file = None 
    st.session_state.data = None
    st.session_state.clear()
    st.success("Files and Past data is cleared successfully!")
    st.session_state.run_rerun = True 

if "run_rerun" in st.session_state and st.session_state.run_rerun:
    st.session_state.run_rerun = False
    st.rerun()
st.button("Clear", on_click=clear )
# Create a button that will check if a file is uploaded
if st.button("Search Jobs 🔍"):
    start()
    st.session_state.jobmatch_resume_file = resume_file 
 