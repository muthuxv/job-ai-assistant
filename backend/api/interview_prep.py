# backend/api/interview_prep.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from models.database import get_db
from models.models import Application, Job, UserCV, UserSettings
from services.interview_prep import InterviewPreparer
from services.cv_parser import CVParser
from services.llm_provider import get_provider, BaseLLMProvider

router = APIRouter()

def get_llm_provider(db: Session = Depends(get_db)) -> BaseLLMProvider:
    settings = db.query(UserSettings).first()
    if settings and settings.api_key:
        return get_provider(settings.provider, settings.api_key)
    return get_provider("gemini", os.getenv("GEMINI_API_KEY"))


@router.get("/{application_id}")
def get_interview_prep(
    application_id: int,
    db: Session = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider)
):
    try:
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise HTTPException(status_code=404, detail="Candidature non trouvée")

        job = db.query(Job).filter(Job.id == application.job_id).first()
        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        if not cv:
            raise HTTPException(status_code=400, detail="Aucun CV actif")

        cv_parser = CVParser(provider)
        user_profile = cv_parser.create_user_profile(cv.parsed_data)

        preparer = InterviewPreparer(provider)
        print(f"🎤 Génération préparation entretien pour : {job.title}")
        prep_data = preparer.generate_questions(job.requirements, user_profile)

        return {
            "application_id": application_id,
            "job_title": job.title,
            "company": job.company,
            "preparation": prep_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))