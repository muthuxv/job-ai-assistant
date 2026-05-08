# backend/services/job_analyzer.py
from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv()

class JobAnalyzer:
    def __init__(self):
        # Force UTF-8 dans la config du client
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options={'headers': {'Content-Type': 'application/json; charset=utf-8'}}
        )
    
    def analyze_job(self, job_description: str) -> dict:
        """
        Analyse une offre d'emploi
        """
        
        # Encode explicitement en UTF-8
        if isinstance(job_description, str):
            job_description = job_description.encode('utf-8').decode('utf-8')
        
        prompt = """Tu es un expert en recrutement tech. Analyse cette offre.

OFFRE D'EMPLOI :
""" + job_description + """

Retourne UNIQUEMENT un JSON valide :
{
  "title": "titre du poste",
  "company": "entreprise",
  "location": "lieu",
  "contract_type": "CDI/CDD/Freelance/Stage",
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "ats_keywords": ["keyword1", "keyword2"],
  "experience_level": "junior/mid/senior/lead",
  "key_responsibilities": ["resp1", "resp2"],
  "required_education": "niveau requis",
  "salary_range": "fourchette",
  "benefits": ["avantage1", "avantage2"],
  "nice_to_have": ["bonus1", "bonus2"]
}"""

        try:
            response = self.client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2500,
                )
            )
            
            content = response.text.strip()
            
            # Nettoie
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                if content.startswith("json"):
                    content = content[4:]
            
            analysis = json.loads(content.strip())
            return analysis
            
        except Exception as e:
            print(f"❌ Erreur : {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def calculate_match_score(self, job_analysis: dict, user_profile: dict) -> dict:
        """
        Calcule le match score
        """
        
        job_json = json.dumps(job_analysis, indent=2, ensure_ascii=False)
        profile_json = json.dumps(user_profile, indent=2, ensure_ascii=False)
        
        prompt = """Expert recrutement. Calcule compatibilite.

OFFRE :
""" + job_json + """

PROFIL :
""" + profile_json + """

Retourne JSON :
{
  "score": 85,
  "strengths": ["force1", "force2"],
  "gaps": ["manque1", "manque2"],
  "recommendations": ["conseil1", "conseil2"],
  "fit_summary": "resume"
}"""

        try:
            response = self.client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )
            
            content = response.text.strip()
            
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            
            return json.loads(content.strip())
            
        except Exception as e:
            print(f"❌ Erreur : {str(e)}")
            raise