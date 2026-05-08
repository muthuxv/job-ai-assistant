# backend/services/cover_letter_generator.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class CoverLetterGenerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
    
    def generate(self, job_analysis: dict, user_profile: dict, tone: str = "formal") -> str:
        tone_guide = {"formal": "Formel", "startup": "Dynamique", "tech": "Technique"}.get(tone, "Formel")
        
        prompt = f"""Lettre de motivation {tone_guide}.

OFFRE : {job_analysis['title']} chez {job_analysis['company']}
CANDIDAT : {user_profile['name']}

Ecris la lettre (300 mots) :"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.7, max_output_tokens=2000)
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Erreur : {e}")
            raise
    
    def generate_multiple_tones(self, job_analysis: dict, user_profile: dict) -> dict:
        return {
            "formal": self.generate(job_analysis, user_profile, "formal"),
            "startup": self.generate(job_analysis, user_profile, "startup"),
            "tech": self.generate(job_analysis, user_profile, "tech")
        }