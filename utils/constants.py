RESUME_PARSERS_PROMPT = """
You are a professional resume parser. Your task is to extract relavant information from resume :{resume_data}.
like Name, email, phone numbers, technical skills, soft skills, job titles, companies, work experience,
education and certifications.
Make sure to extract all the relevant experinece and do not summarize or remove any information. The output resut should be a 
returned in Json format with the following keys:
"name": <name of the candidate>
"email": <email of the candidate>
"phone": <phone number of the candidate>
"summary": <professional summary or objective stated by the candidate>
"skills": <List the skills mentioned in the resume make two sub list one for technical skills and soft skills.
    and provide a score for each skill based on the number of times it is mentioned in the resume.
    for example: "technical_skills": ["name": "skill_name", "confidence": score],
    "soft_skills": ["name": "skill_name", "confidence": score]>
"work_history": <List of work expereince with Company name, job title, start and End date and Location of the job.
with following structure:
["company_name" : <company name>, 
"job_title":<job title>,
"start_date": <start date>,
"end_date" :<end date>,
"location": <location>,
]>
"work_expereince": <for work expereince include total years and key domain experience and 
positions held and achievements with following structure:   
"total_years": approximate_years,
"domains": ["domain1", "domain2", ...],
"positions": ["position1", "position2", ...],
"achievements": ["achievement1", "achievement2", ...]>
education: <List of Degrees, educational qualifications>
certifications: <List of certifications with name, date of certification and issuing authority.>
"""

RESUME_EXTRACT_PROMPT = """You are a professional resume parser. Your task is to extract relavant information from resume :{resume_data}.
like Name, email, phone numbers, technical skills, soft skills, job titles, companies, work experience,
education and certifications. return the respons as a JSON format with following keys:
"name": <name of the candidate>
"email": <email of the candidate>
"phone": <phone number of the candidate>
"summary": <professional summary or objective stated by the candidate>
"skills":<List the skills mentioned in the resume under two sub category one for technical skills and soft skills.> 
"work_history": <List of work expereince with each history with following structure:
                ["company_name" : <company name>, 
                "job_title":<job title>,
                "start_date": <start date>,
                "end_date" :<end date>,
                "location": <location>,
                ]>
"education": <List of Degrees, educational qualifications>
"certifications": <List of certifications with name, date of certification and issuing authority.>
"professional_experience": <for professional work experience include total years, key domain experience and positions held and achievements with following structure:   
                            "total_years": approximate_years,
                            "domains": ["domain1", "domain2", ...],
                            "positions": ["position1", "position2", ...],
                            "achievements": ["achievement1", "achievement2", ...]>
Make sure to extract all the relevant experinece and do not summarize or remove any information from original resume content.
You must return relevant information in a structured format.
"""

JOBDESC_PARSER="""You are a professional job description parser. 
Your task is to extract relavant information from job description: {job_description} as a context.
You can extract job title, company name, job description, key responsibilities, 
required skills, preferred skills, qualifications requirements and any other relevant information.
You must return relevant information in a structured format and do not summarize or remove any informartion.
return result in Json format with the following keys:
"external_job_id": <extract job id or an unique identifier mentioned in the job description>
"job_title": <job title mentioned in the job description>
"company_name": <company name mentioned in the job description> 
"required_experience": <List required years of experience and any specific experience requirements mentioned explicitly.>
"key_responsibilities": <List of key responsibilities mentioned in the job description.>
"required_skills": <List the required skills under two categories <technical skills> and <soft skills> as follows.
                    "technical_skills": <List of technical skills mentioned in the job description.>
                    "soft_skills": <List of soft skills mentioned in the job description example Communication, leadership, teamwork, etc..>
"qualifications": <list the required degrees, certifications, educational qualifications>
"must_haves": <List any other must-have skills or qualifications mentioned in the job description.>
"nice_to_haves": <List of nice-to-have skills or qualifications mentioned in the job description.>
Strictly follow the format and do not fabricate any information outside of the job description context provided.
"""
JD_ADDITION_INSTRUCTIONS= """
For each identified item, assign an importance score from 1-5 where:
    - 5: Explicitly stated as essential/required/must-have
    - 4: Strongly emphasized but not explicitly required
    - 3: Mentioned multiple times or with moderate emphasis
    - 2: Mentioned once without emphasis
    - 1: Implicitly mentioned or inferred"""

ANALYZER_SYSTEM_PROMPT ="""
You are a professional at analyzing resumes and match it with the job description provided
Analyze and evaluate how well this resume matches the job description
Resume:{resume_data}
Job Description:{job_description}
Provide the following:
        1. An overall match score from 0-100
        2. Detailed feedback on candidate strengths against the given job requirements
        3. Specific suggestions and recomendation for how the candidate could improve their resume based on the job description provided
        4. List of any requirements or skills from the job description that are missing from the resume
        5. List Stregths and Weaknesses of the candidate resume which matching against the job description
return result in Json format with following keys: 
"email": <email of the candidate from resume>
"name": <name of the candidate from resume>
"external_job_id": <extract job id or an unique identifier mentioned in the job description>
"overall_score": <An overall match score from 0-100>
"feedback" : <detailed feedback on why the candidate is a good match or not a great match if the score is below 50%>
"suggestions" : <detailed suggestions on how the candidate can improve their resume specific to the provided job description>
"recomendation" :  <detailed recomentdation to improve resume based on the job decription requirements and missings skills>
"gaps" : <List of any requirements or skills from the job description that are missing from the resume>
"weaknesses": <List any weakness of the candidate resume which matching against the job description>
"strengths" : <List the skill strengths of the candidate resume against the job requiremnts in the job description>
your final response must be in JSON format
"""