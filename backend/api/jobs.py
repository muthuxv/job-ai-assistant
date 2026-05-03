# backend/api/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from models.database import get_db
from models.models import Job, Application
from services.job_analyzer import JobAnalyzer

router = APIRouter()
analyzer = JobAnalyzer()

# Pydantic models
class JobCreate(BaseModel):
    description: str
    url: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    requirements: dict
    url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MatchRequest(BaseModel):
    job_id: int
    user_profile: dict

@router.post("/analyze", response_model=dict)
def analyze_job(job: JobCreate, db: Session = Depends(get_db)):
    """
    Analyse une offre d'emploi et l'enregistre
    """
    try:
        print(f"📊 Analyse de l'offre en cours...")
        
        # Analyse avec Claude
        analysis = analyzer.analyze_job(job.description)
        
        print(f"✅ Analyse terminée : {analysis['title']} chez {analysis['company']}")
        
        # Sauvegarde dans DB
        db_job = Job(
            title=analysis["title"],
            company=analysis.get("company", "Non spécifié"),
            description=job.description,
            requirements=analysis,
            url=job.url
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        # Crée automatiquement une application en draft
        db_application = Application(
            job_id=db_job.id,
            status="draft"
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        return {
            "job_id": db_job.id,
            "application_id": db_application.id,
            "analysis": analysis,
            "message": "Offre analysée et enregistrée avec succès"
        }
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    """
    Récupère toutes les offres enregistrées
    """
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Récupère une offre spécifique
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return job

@router.post("/match")
def calculate_match(match_req: MatchRequest, db: Session = Depends(get_db)):
    """
    Calcule le score de match entre une offre et un profil
    """
    try:
        # Récupère l'offre
        job = db.query(Job).filter(Job.id == match_req.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Offre non trouvée")
        
        print(f"🎯 Calcul du match pour : {job.title}")
        
        # Calcul du score
        match_result = analyzer.calculate_match_score(
            job.requirements,
            match_req.user_profile
        )
        
        # Met à jour l'application
        application = db.query(Application).filter(
            Application.job_id == match_req.job_id
        ).first()
        
        if application:
            application.match_score = match_result["score"]
            db.commit()
        
        print(f"✅ Score calculé : {match_result['score']}/100")
        
        return {
            "job_id": match_req.job_id,
            "match_result": match_result
        }
        
    except Exception as e:
        print(f"❌ Erreur calcul match : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """
    Supprime une offre
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Offre supprimée"}