# backend/api/interview_prep.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import Application, Job, UserCV
from services.interview_prep import InterviewPreparer
from services.cv_parser import CVParser

router = APIRouter()
preparer = InterviewPreparer()
cv_parser = CVParser()

@router.get("/{application_id}")
def get_interview_prep(application_id: int, db: Session = Depends(get_db)):
    """
    Génère une préparation d'entretien complète
    """
    try:
        # Récupère l'application
        application = db.query(Application).filter(
            Application.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Candidature non trouvée")
        
        # Récupère le job
        job = db.query(Job).filter(Job.id == application.job_id).first()
        
        # Récupère le CV actif
        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        if not cv:
            raise HTTPException(status_code=400, detail="Aucun CV actif")
        
        user_profile = cv_parser.create_user_profile(cv.parsed_data)
        
        print(f"🎤 Génération préparation entretien pour : {job.title}")
        
        # Génère la préparation
        prep_data = preparer.generate_questions(job.requirements, user_profile)
        
        print(f"✅ {len(prep_data['general_questions'])} questions générales")
        print(f"✅ {len(prep_data['technical_questions'])} questions techniques")
        print(f"✅ {len(prep_data['behavioral_questions'])} questions comportementales")
        
        return {
            "application_id": application_id,
            "job_title": job.title,
            "company": job.company,
            "preparation": prep_data
        }
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))