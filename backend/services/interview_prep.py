# backend/services/interview_prep.py
from services.llm_provider import BaseLLMProvider
import json


class InterviewPreparer:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def generate_questions(self, job_analysis: dict, user_profile: dict) -> dict:
        """
        Génère des questions d'entretien probables et des suggestions de réponses
        """

        prompt = f"""Tu es un expert en préparation d'entretiens. Génère des questions d'entretien probables pour cette candidature.

OFFRE D'EMPLOI :
Poste : {job_analysis['title']}
Entreprise : {job_analysis['company']}
Compétences requises : {', '.join(job_analysis['technical_skills'][:10])}
Responsabilités : {', '.join(job_analysis['key_responsibilities'][:5])}

PROFIL CANDIDAT :
{json.dumps(user_profile, indent=2, ensure_ascii=False)}

Génère UNIQUEMENT un JSON avec cette structure :
{{
  "general_questions": [
    {{
      "question": "question générale",
      "why_asked": "pourquoi cette question",
      "tips": "conseils pour bien répondre",
      "example_answer": "exemple de réponse structurée (pas à réciter tel quel)"
    }}
  ],
  "technical_questions": [
    {{
      "question": "question technique",
      "topic": "sujet technique concerné",
      "tips": "comment l'aborder",
      "key_points": ["point clé 1", "point clé 2"]
    }}
  ],
  "behavioral_questions": [
    {{
      "question": "question comportementale",
      "framework": "méthode STAR recommandée",
      "your_example": "exemple concret du CV du candidat à utiliser"
    }}
  ],
  "questions_to_ask": [
    {{
      "question": "question à poser au recruteur",
      "why": "pourquoi cette question est pertinente",
      "shows": "ce que ça montre de toi"
    }}
  ],
  "red_flags_to_avoid": ["erreur à éviter 1", "erreur 2"],
  "strengths_to_highlight": ["force à mettre en avant 1", "force 2"]
}}

Génère 3-4 questions par catégorie. Base-toi sur le profil réel du candidat pour les exemples."""

        try:
            print(f"🎤 Génération préparation entretien avec {self.provider.__class__.__name__}...")
            return self.provider.generate_json(prompt, temperature=0.5)
        except Exception as e:
            print(f"❌ Erreur génération questions : {e}")
            raise