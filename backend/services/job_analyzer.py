# backend/services/job_analyzer.py
from services.llm_provider import BaseLLMProvider
import json

class JobAnalyzer:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
    
    def analyze_job(self, job_description: str) -> dict:
        prompt = f"""Tu es un expert en recrutement tech. Analyse cette offre d'emploi.

OFFRE D'EMPLOI :
{job_description}

Retourne UNIQUEMENT un objet JSON valide :
{{
  "title": "titre exact du poste",
  "company": "nom de l'entreprise",
  "location": "lieu",
  "contract_type": "CDI/CDD/Freelance/Stage",
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1"],
  "ats_keywords": ["keyword1"],
  "experience_level": "junior/mid/senior/lead",
  "key_responsibilities": ["resp1"],
  "required_education": "niveau requis",
  "salary_range": "fourchette ou Non spécifié",
  "benefits": ["avantage1"],
  "nice_to_have": ["bonus1"]
}}"""

        return self.provider.generate_json(prompt, temperature=0.2)
    
    def calculate_match_score(self, job_analysis: dict, user_profile: dict) -> dict:
        prompt = f"""Tu es un expert en recrutement. Calcule un score de compatibilité.

OFFRE :
{json.dumps(job_analysis, indent=2, ensure_ascii=False)}

PROFIL :
{json.dumps(user_profile, indent=2, ensure_ascii=False)}

Retourne UNIQUEMENT un JSON :
{{
  "score": 85,
  "strengths": ["point fort 1"],
  "gaps": ["lacune 1"],
  "recommendations": ["conseil 1"],
  "fit_summary": "résumé en 2-3 phrases"
}}"""

        return self.provider.generate_json(prompt, temperature=0.3)