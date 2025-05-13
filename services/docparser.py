import re
from sklearn.metrics.pairwise import cosine_similarity
from models.similarity_model import cosine_similarity as ms_cosine_similarity
from services.extractor import (extract_sections_from_resume_text, 
                           extract_entities,
                           combine_lists,
                           get_list_keywords) 
class ResumeParserService:
    """ USing Regex and other tooks extract sections of the resume
    Resume Extraction: Contact(name, phone, email), summary, skills, experience, education 
    parse_resume: returns dict({resume sections})
    """
    def __init__(self, nlp_tool):
        self.__nlp_tool = nlp_tool
        self.err = []
        pass
    def parse_resume(self, raw_resume):
        """ returns the dict({resume sections})"""
        self.raw_resume = raw_resume
        # return all Sections
        self._resume_sections =  extract_sections_from_resume_text(self.raw_resume)
        # list of all skills in skill section
        self.li_resume_skills = get_list_keywords(self._resume_sections.get("skills"))

        #step 1b : extract all resume tokens, ner_entities
        tokens_skill, ner_entities_skill, self.err = extract_entities(self.raw_resume, self.__nlp_tool)

        # Combine all the Spacy -NER tokens 
        self.combo_skills = combine_lists([self.li_resume_skills, 
                                      tokens_skill, 
                                      ner_entities_skill.get("skills",[]),
                                      ner_entities_skill.get("organizations")])
        return {"resume_text": raw_resume,
                "resume_sections" : self._resume_sections,
                "contact" : {"name": self._resume_sections.get("name",""),
                             "phone": self._resume_sections.get("phone",""),
                             "email": self._resume_sections.get("email","")
                             },
                "skills": self._resume_sections.get("skills"),
                "additional_kwds": self.combo_skills}
    
    def get_list_skills(self):
        """returns a a set of all skills extracted from skill section""" 
        return list(set(self.li_resume_skills))
    
    def get_combined_skills(self):
        """returns a a set of all skills extracted from skill section using regex and NER tools
        May not be accurate """
        return self.combo_skills
    

class JDParserService:
    """ Using Regex and other tooks extract keywords of the job description.
    parse_jobdesc: return list of keywords that are matched using nlp : skills, education, organizations
    """
    def __init__(self, nlp_tool):
        self.__nlp_tool = nlp_tool
        self.err = []
        pass

    def parse_jobdesc(self, raw_jobdesc):
        """ return list of keywords that are matched using nlp : skills, education, organizations"""
        self.raw_jobdesc = raw_jobdesc
        tokens_jobreq, ner_entities_jobreq, self.err = extract_entities(self.raw_jobdesc, self.__nlp_tool)
        
        # Combine all the Spacy -NER tokens 
        self.jdkeywords = combine_lists([ner_entities_jobreq.get("skills",[]),
                                      ner_entities_jobreq.get("education",[]),
                                      ner_entities_jobreq.get("organizations",[])])
        return {"job_description" : raw_jobdesc,
                "keywords" : self.jdkeywords}
    
    def get_keywords(self):
        return self.jdkeywords
    

class MatchKeywordsService:    
    """ Get Keword Matching Score : use vectorizer to get Cosine Similarity between Keywords from Job Description against Skills from Resume
        Get Semantic Matching score:  use Embeddings to see the semantic matcing score.
    """
    def __init__(self, nlp_tool, vectorizer, embedding_model):
        self.__nlp_tool = nlp_tool
        self.__vectorizer = vectorizer
        self.__embedding_model = embedding_model
        self.err = []
        pass
    
    def match_skills(self, raw_resume, raw_jobdesc): 
        self.raw_resume = raw_resume
        self.raw_jobdesc = raw_jobdesc
        self.__resume_parser = ResumeParserService(self.__nlp_tool)
        self.sections= self.__resume_parser.parse_resume(self.raw_resume )
        self.resume_skills =self.__resume_parser.get_list_skills()
        self.__jobdesc_parser = JDParserService(self.__nlp_tool)
        self.jdkeywords= self.__jobdesc_parser.parse_jobdesc(self.raw_jobdesc)

        return self.__calculate_scores()
    
    def get_resume_sections(self):
        self.__resume_parser._resume_sections
    def get_resume_skills_kwds(self):
        """ returns resume skills and keywords extracted from resume."""
        return self.__resume_parser.get_combined_skills()
    def get_resume_skills(self):
        """ returns resume sections with skills listed"""
        return self.__resume_parser.get_list_skills()
    def get_jobdesckwds(self): 
        return self.__jobdesc_parser.get_keywords()


    def __calculate_scores(self):
        try:
            # #####print("Combo Skills:")
            # #####print(self.__resume_parser.get_combined_skills()) 
            docs = []
            docs.append(", ".join(self.__resume_parser.get_combined_skills()))

            # #####print("self.jdkeywords:")
            # #####print(self.jdkeywords)
            docs.append(", ".join(self.jdkeywords))
            # #####print(docs)
            vectors = self.__vectorizer.get_embedding(docs)
            cos_sim = cosine_similarity(vectors)[0][1]
            self.__match_percentage = round(cos_sim * 100, 2) 
        except Exception as e:
            print(f"Error calculating match percentage: {e}")

        resume_embedding = self.__embedding_model.get_embedding(self.raw_resume)
        job_embedding = self.__embedding_model.get_embedding(self.raw_jobdesc)  
        
        self.__ms_cs_score= round(ms_cosine_similarity(resume_embedding, job_embedding)*100,2)
        self.__similarity_score = round((cosine_similarity([resume_embedding.cpu().numpy()], [job_embedding.cpu().numpy()])[0][0])*100,2)
        
        #####print(f"exact_match {self.__match_percentage:.2f}"),
        #####print(f"similarity_score {self.__similarity_score:.2f}") 
        # #####print(f"ms_cs_score {self.__ms_cs_score:.2f}")

        return self.get_scores()
    
    def get_scores(self):
        return {"exact_match": f"{self.__match_percentage:.2f}",
                "similarity_score" : f"{self.__similarity_score:.2f}", 
                "ms_cs_score": f"{self.__ms_cs_score:.2f}"} 

 