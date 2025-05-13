import json
import pandas as pd
import streamlit as st
import requests
import os
from streamlit_extras.colored_header import colored_header
API_URL= os.environ.get('FASTAPI_URL', "http://localhost:8000")
 
st.set_page_config(
    page_title="Recruiter Hub: Scoring Assistant",
    page_icon="👔",    
    layout="wide",
    initial_sidebar_state="expanded"
) 
# # Create a sidebar for navigation
# st.sidebar.title("Navigation")  
# page = st.sidebar.radio("Go to", [ "Resume-Job Matcher"])
#                         #,"Recruiter Dashboard", "MatchMyJob", "MatchMyCandidate"])

st.session_state.resume_file =  None
st.session_state.jobdesc_file = None
st.session_state.data = None

if "run_rerun" not in st.session_state:
    st.session_state.run_rerun = False
elif "run_rerun" in st.session_state and st.session_state.run_rerun:
    st.session_state.run_rerun = False
    st.rerun()
    
 
st.title("Resume-Job Matcher")
st.subheader("Upload your resume and Job description for ATS evaluation")

 
col1, col2 = st.columns(2)
col1.subheader("Resume")
col1.write("Upload your resume file here.")
resume_file = col1.file_uploader("Choose a resume file", type=["pdf", "docx"])
st.session_state.resume_file = resume_file
# Upload JD
col2.subheader("Job Description")
col2.write("Upload your job description file here.")
jobdesc_file = col2.file_uploader("Choose a job desciption file", type=["pdf", "docx", ".txt"])
st.session_state.jobdesc_file = jobdesc_file

def display_resume_job_analysis(data):
    # Detailed analysis with tabs
    if data is None:
        if st.session_state.data is not None :
            data = st.session_state.data
        else:
            return
    tab1, tab2, tab3, tab4 = st.tabs(["Scores", "Skills Analysis", "Feedback", "Improvement Suggestions"])
    
    with tab1:
        tab1_col1 , tab1_col2 , tab1_col3= st.columns(3)
        colored_header(
            label="Resume Scores",
            description="Detailed scores for the resume analysis",
            color_name="blue-70"
        ) 
        tab1_col1.metric("Skills Match", f"{data.get('scores',{}).get('exact_match',0)}%")
        tab1_col2.metric("Similarity Match", f"{data.get('scores',{}).get('similarity_score',0)}%")
        tab1_col3.metric("Overall Match", f"{data.get('scores',{}).get('overall_score',0)}%")
    
    
    with tab2:
        colored_header(
            label="Resume Feedback Analysis",
            description="Key strengths and improvement areas identified",
            color_name="yellow-80"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Strengths 💪")
            for strength in data.get('strengths', []):
                st.success(strength)
        
        with col2:
            st.markdown("### Areas for Improvement 🔍")
            for weakness in data.get('weaknesses', []):
                st.warning(weakness)

        with col3:
            st.markdown("### Suggestions 💡")
            for suggestion in data.get('gaps', []):
                st.info(suggestion) 

    with tab3:
        colored_header(
            label="Resume Feedback Analysis",
            description="Detailed feedback for the resume",
            color_name="red-70"
        )
        st.markdown("### Feedback ")
        st.write(data.get('feedback', "No feedback available"))

    with tab4:
        colored_header(
            label="Resume Improvement Suggestions",
            description="Suggestions for improving the resume",
            color_name="green-70"
        )
        st.markdown("### Suggestions")
        st.write(data.get('suggestions', "No suggestions available"))

        st.markdown("### Recommendations")  
        st.write(data.get('recomendation', "No recommendations available"))

def start(resume_file=None, jobdesc_file=None):
    if not (resume_file or jobdesc_file):
        st.error("Files not provided. Upload Resume and Job Description") 
        return
    if resume_file is None:
        st.error("Resume file not provided. Upload Resume") 
        return
    if jobdesc_file is None:
        st.error("Job Description file not provided. Upload Job Description") 
        return
    if resume_file and jobdesc_file:
        st.success("Files uploaded successfully!")
        with st.spinner("Analyzing resume...Wait for it...", show_time=True):      
            if jobdesc_file:
                files = {"resume_file": (resume_file.name, resume_file.getvalue(), resume_file.type),
                            "jobdesc_file": (jobdesc_file.name ,jobdesc_file.getvalue(), jobdesc_file.type)}

            response = requests.post(f"{API_URL}/analyze-resume", files=files)
            # Display results (assuming the result is a structured JSON or similar)
            if response.status_code == 200:
                data = response.json()
                st.sidebar.header("Resume ATS Scoring Results") 
                try:
                    if not isinstance(data, dict):   
                        st.error("Invalid response format. Expected a dictionary.")
                        st.markdown(f"response.status_code: \n{response.status_code}")
                        st.markdown(f"data: \n{data} | data type {type(data)}")

                    if isinstance(data, dict):
                        st.session_state.data = data
                        display_resume_job_analysis(data)
                        # # Display the results on the page 
                        # col1, col2, col3 = st.columns(3)
                        # st.subheader("Resume Skills Match")
                        # col1.metric("Skills Match", f"{data.get('scores',{}).get('exact_match',0)}%")
                        # col2.metric("Similarity Match", f"{data.get('scores',{}).get('similarity_score',0)}%")
                        # col3.metric("Overall Match", f"{data.get('scores',{}).get('overall_score',0)}%")


                except Exception as e:
                    st.error(f"response.status_code: \n{response.status_code}. exception : {e}")
                    #####print("Data", data)

def clear():
    st.session_state.resume_file = None
    st.session_state.jobdesc_file = None
    st.session_state.data = None
    st.session_state.clear()
    st.success("Files and Past data is cleared successfully!")

    st.session_state.run_rerun = True 

if "run_rerun" in st.session_state and st.session_state.run_rerun:
    st.session_state.run_rerun = False
    st.rerun()
if st.session_state.data is None:
    st.button("Start Analysis", on_click=start, args=(resume_file, jobdesc_file)) 
st.button("Clear", on_click=clear )
