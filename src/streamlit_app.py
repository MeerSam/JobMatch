
import json
import pandas as pd
import streamlit as st
import requests
import os
from streamlit_extras.colored_header import colored_header
API_URL= os.environ.get('FASTAPI_URL', "http://localhost:8000")

home_page = st.Page("../pages/home.py", title="Home", icon=":material/house:")
dashboard_page = st.Page("../pages/dashboard.py", title="Dashboard", icon=":material/dashboard:")
jobmatch_page = st.Page("../pages/jobmatch.py", title="JobMatch", icon="✨")
candidate_page = st.Page("../pages/candidatematch.py", title="CandidateMatch", icon="👔")

pg = st.navigation(
    {"Home": [home_page],
     "Dashboard": [dashboard_page],
     "JobMatch": [jobmatch_page],
     "CandidateMatch": [candidate_page]} )
 

pg.run()  
 
