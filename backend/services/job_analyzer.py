# backend/services/job_analyzer.py
from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv()

class JobAnalyzer:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def analyze_job(self, job_description: str) -> dict:
        """
        Analyse une offre d'emploi et extrait toutes les infos importantes
        """
        
        prompt = f"""Tu es un expert en recrutement tech. Analyse cette offre d'emploi et extrais les informations suivantes.

OFFRE D'EMPLOI :
{job_description}

Retourne UNIQUEMENT un objet JSON valide (pas de markdown, pas de ```json) :
{{
  "title": "titre exact du poste",
  "company": "nom de l'entreprise (ou 'Non spécifié' si absent)",
  "location": "lieu (ou 'Non spécifié')",
  "contract_type": "CDI/CDD/Freelance/Stage (ou 'Non spécifié')",
  "technical_skills": ["compétence technique 1", "compétence technique 2"],
  "soft_skills": ["soft skill 1", "soft skill 2"],
  "ats_keywords": ["mot-clé important 1", "mot-clé 2"],
  "experience_level": "junior/mid/senior/lead",
  "key_responsibilities": ["responsabilité 1", "responsabilité 2"],
  "required_education": "niveau requis (ou 'Non spécifié')",
  "salary_range": "fourchette si mentionnée (ou 'Non spécifié')",
  "benefits": ["avantage 1", "avantage 2"],
  "nice_to_have": ["compétence bonus 1", "compétence bonus 2"]
}}

Sois précis et extrait TOUT ce qui est pertinent."""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2500,
                )
            )
            
            content = response.text.strip()
            
            # Enlève les ```json si présents
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                if content.startswith("json"):
                    content = content[4:]
            
            analysis = json.loads(content.strip())
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON : {e}")
            print(f"Réponse brute : {response.text[:500]}")
            raise
        except Exception as e:
            print(f"❌ Erreur analyse : {e}")
            raise
    
    def calculate_match_score(self, job_analysis: dict, user_profile: dict) -> dict:
        """
        Calcule un score de match entre l'offre et le profil du candidat
        """
        
        prompt = f"""Tu es un expert en recrutement. Calcule un score de compatibilité entre ce profil candidat et cette offre.

OFFRE D'EMPLOI :
{json.dumps(job_analysis, indent=2, ensure_ascii=False)}

PROFIL CANDIDAT :
{json.dumps(user_profile, indent=2, ensure_ascii=False)}

Analyse en profondeur et retourne UNIQUEMENT un JSON :
{{
  "score": 85,
  "strengths": ["point fort 1 avec justification", "point fort 2"],
  "gaps": ["manque 1 avec impact", "manque 2"],
  "recommendations": ["conseil actionnable 1", "conseil 2"],
  "fit_summary": "résumé en 2-3 phrases du fit global"
}}

Le score doit être entre 0 et 100. Sois réaliste et constructif."""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
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
                if content.startswith("json"):
                    content = content[4:]
            
            result = json.loads(content.strip())
            return result
            
        except Exception as e:
            print(f"❌ Erreur calcul match : {e}")
            raise