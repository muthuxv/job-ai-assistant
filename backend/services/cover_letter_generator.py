# backend/services/cover_letter_generator.py
from services.llm_provider import BaseLLMProvider
import json


class CoverLetterGenerator:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def generate(
        self,
        job_analysis: dict,
        user_profile: dict,
        tone: str = "formal"
    ) -> str:
        """
        Génère une cover letter personnalisée

        Args:
            job_analysis: Analyse de l'offre d'emploi
            user_profile: Profil du candidat (CV parsé)
            tone: 'formal', 'startup', ou 'tech'
        """

        tone_instructions = {
            "formal": """
Ton : Formel et professionnel
Structure : Lettre de motivation classique française
Style : Respectueux, sobre, élégant
Vocabulaire : Soutenu mais accessible
Longueur : 300-350 mots
Format : Introduction, 2-3 paragraphes de corps, conclusion
""",
            "startup": """
Ton : Dynamique et authentique
Structure : Plus libre, conversationnelle
Style : Enthousiaste, direct, énergique
Vocabulaire : Moderne, tech-friendly
Longueur : 250-300 mots
Format : Accroche forte, pourquoi moi + pourquoi vous, call-to-action
""",
            "tech": """
Ton : Technique et pragmatique
Structure : Focus sur les compétences et réalisations
Style : Concis, orienté résultats, factuel
Vocabulaire : Technique, précis
Longueur : 250-300 mots
Format : Contexte rapide, compétences matchées, projets pertinents, fit technique
"""
        }

        tone_guide = tone_instructions.get(tone, tone_instructions["formal"])

        prompt = f"""Tu es un expert en rédaction de lettres de motivation. Écris une lettre de motivation personnalisée et convaincante.

OFFRE D'EMPLOI :
Poste : {job_analysis['title']}
Entreprise : {job_analysis['company']}
Compétences requises : {', '.join(job_analysis['technical_skills'][:8])}
Responsabilités clés : {', '.join(job_analysis['key_responsibilities'][:5])}

PROFIL CANDIDAT :
Nom : {user_profile['name']}
Résumé : {user_profile['summary']}
Expérience : {user_profile['years_of_experience']} ans
Compétences techniques : {json.dumps(user_profile['technical_skills'], ensure_ascii=False)}
Expériences récentes : {json.dumps(user_profile['recent_experience'][:2], ensure_ascii=False)}
Projets notables : {json.dumps(user_profile['projects'][:2], ensure_ascii=False)}

INSTRUCTIONS DE TON ET STYLE :
{tone_guide}

RÈGLES IMPORTANTES :
1. Personnalise au maximum en mentionnant des éléments CONCRETS du CV
2. Fais le lien entre l'expérience du candidat et les besoins de l'entreprise
3. Quantifie les réalisations quand possible (utilisateurs, %, temps, etc.)
4. Montre l'enthousiasme sans en faire trop
5. Termine par un appel à l'action clair
6. PAS de formules bateau ou de phrases génériques
7. NE MENTIONNE PAS de salaire ou d'avantages
8. Écris en français impeccable

La lettre doit commencer par "Madame, Monsieur," (ou variant selon le ton) et se terminer par une formule de politesse adaptée.

Écris maintenant la lettre de motivation complète :"""

        try:
            print(f"✍️  Génération cover letter ({tone}) avec {self.provider.__class__.__name__}...")
            return self.provider.generate(prompt, temperature=0.7, max_tokens=2000)
        except Exception as e:
            print(f"❌ Erreur génération cover letter : {e}")
            raise

    def generate_multiple_tones(
        self,
        job_analysis: dict,
        user_profile: dict
    ) -> dict:
        """
        Génère 3 versions avec différents tons
        """
        print("📝 Génération cover letter ton formel...")
        formal = self.generate(job_analysis, user_profile, "formal")

        print("📝 Génération cover letter ton startup...")
        startup = self.generate(job_analysis, user_profile, "startup")

        print("📝 Génération cover letter ton tech...")
        tech = self.generate(job_analysis, user_profile, "tech")

        return {
            "formal": formal,
            "startup": startup,
            "tech": tech
        }