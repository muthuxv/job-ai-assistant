# backend/services/interview_prep.py
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class InterviewPreparer:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
    
    def generate_questions(self, job_analysis: dict, user_profile: dict) -> dict:
        prompt = f"""Questions entretien.

OFFRE : {job_analysis['title']}

Retourne JSON avec general_questions, technical_questions, behavioral_questions, questions_to_ask, red_flags_to_avoid, strengths_to_highlight."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.5, max_output_tokens=4000)
            )

            content = response.text.strip()

            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                if content.startswith("json"):
                    content = content[4:]

            return json.loads(content.strip())
        except Exception as e:
            print(f"❌ Erreur : {e}")
            raise