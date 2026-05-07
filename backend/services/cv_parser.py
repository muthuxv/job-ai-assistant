# backend/services/cv_parser.py
from google import genai
from google.genai import types
from pypdf import PdfReader
import os
import json
from dotenv import load_dotenv

load_dotenv()

class CVParser:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrait le texte brut d'un PDF
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"❌ Erreur extraction PDF : {e}")
            raise
    
    def parse_cv(self, cv_text: str) -> dict:
        """
        Parse le CV et extrait toutes les informations structurées
        """
        
        prompt = f"""Tu es un expert en analyse de CV. Parse ce CV et extrais TOUTES les informations importantes.

CV :
{cv_text}

Retourne UNIQUEMENT un JSON valide (pas de markdown, pas de ```json) :
{{
  "personal_info": {{
    "name": "nom complet",
    "email": "email si présent",
    "phone": "téléphone si présent",
    "location": "ville/pays",
    "linkedin": "URL LinkedIn si présent",
    "github": "URL GitHub si présent",
    "portfolio": "URL portfolio si présent"
  }},
  "summary": "résumé professionnel ou objectif en 2-3 phrases",
  "experience": [
    {{
      "title": "titre du poste",
      "company": "nom entreprise",
      "duration": "période",
      "location": "lieu si mentionné",
      "responsibilities": ["responsabilité 1", "responsabilité 2"],
      "achievements": ["réalisation 1", "réalisation 2"]
    }}
  ],
  "education": [
    {{
      "degree": "diplôme",
      "institution": "école/université",
      "year": "année",
      "field": "domaine"
    }}
  ],
  "technical_skills": {{
    "languages": ["langage 1", "langage 2"],
    "frameworks": ["framework 1"],
    "tools": ["outil 1"],
    "databases": ["database 1"],
    "other": ["autre 1"]
  }},
  "soft_skills": ["soft skill 1"],
  "languages": [
    {{
      "language": "langue",
      "level": "niveau"
    }}
  ],
  "projects": [
    {{
      "name": "nom",
      "description": "description",
      "technologies": ["tech 1"],
      "url": "lien"
    }}
  ],
  "certifications": [],
  "interests": []
}}

Sois exhaustif et précis."""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=4000,
                )
            )
            
            content = response.text.strip()
            
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                if content.startswith("json"):
                    content = content[4:]
            
            parsed_cv = json.loads(content.strip())
            return parsed_cv
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON parsing CV : {e}")
            print(f"Réponse : {response.text[:500]}")
            raise
        except Exception as e:
            print(f"❌ Erreur parsing CV : {e}")
            raise
    
    def create_user_profile(self, parsed_cv: dict) -> dict:
        """
        Crée un profil utilisateur simplifié
        """
        return {
            "name": parsed_cv["personal_info"]["name"],
            "summary": parsed_cv["summary"],
            "years_of_experience": len(parsed_cv["experience"]),
            "technical_skills": parsed_cv["technical_skills"],
            "soft_skills": parsed_cv["soft_skills"],
            "education": parsed_cv["education"],
            "recent_experience": parsed_cv["experience"][:2] if parsed_cv["experience"] else [],
            "projects": parsed_cv["projects"][:3] if parsed_cv["projects"] else []
        }