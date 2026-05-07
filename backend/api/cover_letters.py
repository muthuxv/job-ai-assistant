# backend/api/cover_letters.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from models.database import get_db
from models.models import CoverLetter, Application, Job, UserCV
from services.cover_letter_generator import CoverLetterGenerator
from services.cv_parser import CVParser

router = APIRouter()
generator = CoverLetterGenerator()
cv_parser = CVParser()

class CoverLetterRequest(BaseModel):
    application_id: int
    tone: str = "formal"  # formal, startup, tech

class CoverLetterResponse(BaseModel):
    id: int
    content: str
    tone: str
    
    class Config:
        from_attributes = True

@router.post("/generate", response_model=dict)
def generate_cover_letter(
    request: CoverLetterRequest,
    db: Session = Depends(get_db)
):
    """
    Génère une cover letter pour une candidature
    """
    try:
        # Récupère l'application
        application = db.query(Application).filter(
            Application.id == request.application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Candidature non trouvée")
        
        # Récupère le job
        job = db.query(Job).filter(Job.id == application.job_id).first()
        
        # Récupère le CV actif
        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        if not cv:
            raise HTTPException(status_code=400, detail="Aucun CV actif. Uploadez d'abord votre CV.")
        
        # Crée le profil utilisateur
        user_profile = cv_parser.create_user_profile(cv.parsed_data)
        
        print(f"✍️  Génération cover letter pour : {job.title}")
        
        # Génère la cover letter
        cover_letter_text = generator.generate(
            job.requirements,
            user_profile,
            request.tone
        )
        
        # Sauvegarde dans DB
        db_cover_letter = CoverLetter(
            application_id=application.id,
            content=cover_letter_text,
            tone=request.tone
        )
        db.add(db_cover_letter)
        db.commit()
        db.refresh(db_cover_letter)
        
        print(f"✅ Cover letter générée (tone: {request.tone})")
        
        return {
            "cover_letter_id": db_cover_letter.id,
            "content": cover_letter_text,
            "tone": request.tone,
            "message": "Cover letter générée avec succès"
        }
        
    except Exception as e:
        print(f"❌ Erreur génération : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-all-tones", response_model=dict)
def generate_all_tones(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Génère 3 versions (formal, startup, tech)
    """
    try:
        application = db.query(Application).filter(
            Application.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Candidature non trouvée")
        
        job = db.query(Job).filter(Job.id == application.job_id).first()
        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        
        if not cv:
            raise HTTPException(status_code=400, detail="Aucun CV actif")
        
        user_profile = cv_parser.create_user_profile(cv.parsed_data)
        
        print(f"✍️  Génération 3 versions pour : {job.title}")
        
        # Génère les 3 versions
        all_versions = generator.generate_multiple_tones(
            job.requirements,
            user_profile
        )
        
        # Sauvegarde toutes les versions
        saved_ids = {}
        for tone, content in all_versions.items():
            db_cover_letter = CoverLetter(
                application_id=application.id,
                content=content,
                tone=tone
            )
            db.add(db_cover_letter)
            db.commit()
            db.refresh(db_cover_letter)
            saved_ids[tone] = db_cover_letter.id
        
        print(f"✅ 3 versions générées")
        
        return {
            "cover_letters": all_versions,
            "ids": saved_ids,
            "message": "3 versions générées avec succès"
        }
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/application/{application_id}")
def get_cover_letters_for_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère toutes les cover letters d'une candidature
    """
    cover_letters = db.query(CoverLetter).filter(
        CoverLetter.application_id == application_id
    ).all()
    
    return cover_letters