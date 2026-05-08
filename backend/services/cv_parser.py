# backend/services/cv_parser.py
from pypdf import PdfReader
from services.llm_provider import BaseLLMProvider

class CVParser:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

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
      "duration": "période (ex: 'Jan 2022 - Présent')",
      "location": "lieu si mentionné",
      "responsibilities": ["responsabilité 1", "responsabilité 2"],
      "achievements": ["réalisation quantifiée 1", "réalisation 2"]
    }}
  ],
  "education": [
    {{
      "degree": "diplôme",
      "institution": "école/université",
      "year": "année ou période",
      "field": "domaine d'études"
    }}
  ],
  "technical_skills": {{
    "languages": ["langage 1", "langage 2"],
    "frameworks": ["framework 1", "framework 2"],
    "tools": ["outil 1", "outil 2"],
    "databases": ["database 1", "database 2"],
    "other": ["autre compétence 1", "autre 2"]
  }},
  "soft_skills": ["soft skill 1", "soft skill 2"],
  "languages": [
    {{
      "language": "langue",
      "level": "niveau (natif/courant/intermédiaire/notions)"
    }}
  ],
  "projects": [
    {{
      "name": "nom du projet",
      "description": "description courte",
      "technologies": ["tech 1", "tech 2"],
      "url": "lien si présent"
    }}
  ],
  "certifications": ["certification 1", "certification 2"],
  "interests": ["intérêt 1", "intérêt 2"]
}}

Sois exhaustif et précis. Si une info n'est pas présente, mets une liste vide [] ou une string vide ""."""

        try:
            print(f"🧠 Parsing CV avec {self.provider.__class__.__name__}...")
            return self.provider.generate_json(prompt, temperature=0.1)
        except Exception as e:
            print(f"❌ Erreur parsing CV : {e}")
            raise

    def create_user_profile(self, parsed_cv: dict) -> dict:
        """
        Crée un profil utilisateur simplifié pour le matching
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