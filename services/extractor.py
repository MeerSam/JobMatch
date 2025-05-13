import re


def extract_sections_from_resume_text(text):
    """Extract sections from the resume text.
    returns dict with following keys :"name", "email", "phone"
    "summary", "skills", "experience", "education"                        
    """
    sections={}
    # Define regex patterns for different sections
    contact_patterns ={ "name": r"^[A-Z][a-zA-Z\s]+$",
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "phone": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",}
    patterns = {
        "summary": r"^((professional\s*)?Summary|Profile|Objective)[\b\s\:]*?",
        "education": r"^(Education|Degree|University|College)[\s\:]*?",
        "experience": r"^(\bWork\s*(experience|history)\b|Experience\b|Employment History\b)[\s\:]*?$",
        "skills": r"^(Skills|Technical Skills|Core Competencies)[\s\:]*?$",
    }

    # Split text into lines
    lines = text.split("\n")
    curr_section= None

    for line in lines:
        if line.strip() == "":
            continue # Skip empty lines

        # Check if the line matches any of the section patterns
 
        for section_name , pattern in patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                curr_section= section_name
                # #####print(f"Section found: {curr_section}\n\n\n\n")
                if section_name not in sections:
                    sections[curr_section] = []

        if curr_section is None:
            match_name = re.search(contact_patterns["name"], line)
            match_email = re.search(contact_patterns["email"], line)
            match_phone = re.search(contact_patterns["phone"], line)
            if  "name" not in sections and match_name:
                sections["name"] = match_name.group(0)

            if "email" not in sections and match_email:
                sections["email"] = match_email.group(0)

            if "phone" not in sections and match_phone:
                sections["phone"] = match_phone.group(0)
            continue
        else:
            sections[curr_section].append(line.strip())
    # #####print(f"Done\n\n\n")
    # #####print(sections.keys())
    for section in sections:
        if section in ["name", "email", "phone"]:
            continue
        sections[section] = "\n".join(sections[section])

    #remove empty sections
    return sections

def get_list_keywords(text):
  try:
    delimiters =["\n",","] #split based on delimeter
    regex_pattern = '|'.join(map(re.escape, delimiters))
    if type(text) == str:
        listofskills= re.split(regex_pattern, text)
        for i, keyword in enumerate(listofskills):
            keyword = re.sub(r"[\w\W\s\S]*[\:\-]", "", keyword)
            listofskills[i] = keyword.strip()
        return listofskills
    elif type(text) == list:
        return text
    else:
        return []
  except Exception as e:
      pass 

def extract_entities(text, tool={'name': None,
                                  'tool': None} ):
    """Extract entities using the specified tool
    tool={'name': None,'tool': None}"""
    error=None 
    # Load the NER model (e.g., spaCy, Hugging Face Transformers, etc.) 
    try:
        if tool.get('name') == "spacy":            
            return extract_entities_using_spacy(text, tool.get('tool'))
        elif tool == "ner_tool":
            return extract_entities_using_ner_tool(text, tool.get('tool'))
        else:
            raise ValueError("Invalid tool specified. Use 'spacy' or 'ner_tool'.")
    except Exception as e:
        return None, f"Error while extracting entities:{e}"
  
def extract_entities_using_ner_tool(text, ner_pipeline):
    """Extract sections from the resume text using NER tool""" 
    # Extract entities
    entities = ner_pipeline(text)

    #####print("Extracted Entities:")
    for entity in entities:
        print(f"{entity['word']} ({entity['entity']})")

def extract_entities_using_spacy(text, nlp_tool):
    try: 
        doc = nlp_tool(text.lower())
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        entities = {"experience": [],
                    "education": [], 
                    "skills": [],
                    'organizations': [],
                    'dates': [],
                    'degrees': [],
                    'job_titles': []}
        
        degree_patterns = ["Bachelor", "Master", "PhD", "BS", "MS", "MBA"]   
        for pattern in degree_patterns:
            if re.search(r'\b' + re.escape(pattern) + r'\b', text):
                entities['degrees'].append(pattern)
        for ent in doc.ents:
            if ent.label_ == "ORG":  # Organizations (Universities/Companies)
                entities["organizations"].append(ent.text)
            elif ent.label_ in ["DATE", "CARDINAL"]:  # Dates/Numbers (Years worked)
                entities["dates"].append(ent.text) 
            elif ent.label_ == "":
                entities["skills"].append(ent.text) 

        return tokens, entities, None
    except Exception as e:
        return None, f"Error while extracting entites using spaCy: {e}"
 
def combine_lists(lists:list):
    combined_list = []   
    for li in lists: 
      if type(li)==list: 
        for item in li:
          if item not in combined_list: 
            combined_list.append(item.lower().strip())
      elif type(li)==str: 
        for item in li.split(","):
            if item not in combined_list: 
                combined_list.append(item.lower().strip())
    return set(combined_list)  
