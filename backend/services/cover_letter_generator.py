# backend/services/cover_letter_generator.py
from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv()

class CoverLetterGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def generate(self, job_analysis: dict, user_profile: dict, tone: str = "formal") -> str:
        """
        Génère une cover letter personnalisée
        """
        
        tone_instructions = {
            "formal": "Ton formel et professionnel. Structure classique française. 300-350 mots.",
            "startup": "Ton dynamique et authentique. Style conversationnel. 250-300 mots.",
            "tech": "Ton technique et pragmatique. Focus compétences. 250-300 mots."
        }
        
        tone_guide = tone_instructions.get(tone, tone_instructions["formal"])
        
        prompt = f"""Tu es un expert en rédaction de lettres de motivation. Écris une lettre personnalisée et convaincante.

OFFRE : {job_analysis['title']} chez {job_analysis['company']}
Compétences requises : {', '.join(job_analysis['technical_skills'][:8])}
Responsabilités : {', '.join(job_analysis['key_responsibilities'][:5])}

CANDIDAT : {user_profile['name']}
Résumé : {user_profile['summary']}
Expérience : {user_profile['years_of_experience']} ans
Compétences : {json.dumps(user_profile['technical_skills'], ensure_ascii=False)}

STYLE : {tone_guide}

RÈGLES :
- Personnalise avec des éléments CONCRETS du CV
- Fais le lien entre expérience et besoins de l'entreprise
- Quantifie les réalisations
- Termine par un appel à l'action
- En français impeccable

Écris la lettre complète :"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Erreur : {e}")
            raise
    
    def generate_multiple_tones(self, job_analysis: dict, user_profile: dict) -> dict:
        """
        Génère 3 versions
        """
        print("📝 Génération 3 versions...")
        return {
            "formal": self.generate(job_analysis, user_profile, "formal"),
            "startup": self.generate(job_analysis, user_profile, "startup"),
            "tech": self.generate(job_analysis, user_profile, "tech")
        }