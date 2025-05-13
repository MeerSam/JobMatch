# JobMatch
AI Powered Resume Analyzer


## How to Run

#### Step 1: Create a Virtual Environment

`python -m venv .venv`

#### Step 2: Activate the Virtual Environment

```
    .venv\Scripts\activate # For Windows

    source .venv/bin/activate # For Linux/MacOS

    .venv\Scripts\Activate.ps1 # for PowerShell
```

#### Step 3: Install Dependencies from requirements.txt
```
pip install -r requirements.txt
```
#### Info:
    ```pip freeze > requirements.txt```

    <!-- pip freeze is a command that lists all installed Python packages along with their versions in your current environment.  -->



#### Running Streamlit

```
streamlit run .\src\streamlit_app.py
```

#### Running FASTAPI

#### Start your API server:

```
uvicorn main:app --reload
# or
uvicorn main:app --host 0.0.0.0 --port 8000

```

##### You can now send POST requests with resume text to the FAST API Server from streamlit app
