# backend/api/applications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from models.database import get_db
from models.models import Application, Job, CoverLetter

from services.analytics import Analytics


router = APIRouter()

# Pydantic models
class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    status: str
    match_score: Optional[float]
    applied_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    job: dict
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[dict])
def get_all_applications(db: Session = Depends(get_db)):
    """
    Récupère toutes les candidatures avec les infos du job
    """
    applications = db.query(Application).order_by(Application.created_at.desc()).all()
    
    result = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        
        # Compte les cover letters
        cover_letters_count = db.query(CoverLetter).filter(
            CoverLetter.application_id == app.id
        ).count()
        
        result.append({
            "id": app.id,
            "job_id": app.job_id,
            "status": app.status,
            "match_score": app.match_score,
            "applied_date": app.applied_date,
            "notes": app.notes,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "url": job.url
            },
            "cover_letters_count": cover_letters_count
        })
    
    return result

@router.get("/{application_id}", response_model=dict)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """
    Récupère une candidature avec tous les détails
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Candidature non trouvée")
    
    job = db.query(Job).filter(Job.id == application.job_id).first()
    cover_letters = db.query(CoverLetter).filter(
        CoverLetter.application_id == application_id
    ).all()
    
    return {
        "id": application.id,
        "status": application.status,
        "match_score": application.match_score,
        "applied_date": application.applied_date,
        "notes": application.notes,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
        "job": {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "requirements": job.requirements,
            "url": job.url
        },
        "cover_letters": [
            {
                "id": cl.id,
                "tone": cl.tone,
                "content": cl.content,
                "created_at": cl.created_at
            }
            for cl in cover_letters
        ]
    }

@router.patch("/{application_id}")
def update_application(
    application_id: int,
    update: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une candidature (statut, notes, date)
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Candidature non trouvée")
    
    # Update fields
    if update.status:
        application.status = update.status
    if update.notes is not None:
        application.notes = update.notes
    if update.applied_date:
        application.applied_date = update.applied_date
    
    application.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(application)
    
    return {
        "message": "Candidature mise à jour",
        "application": {
            "id": application.id,
            "status": application.status,
            "notes": application.notes,
            "applied_date": application.applied_date
        }
    }

@router.delete("/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    """
    Supprime une candidature (et son job associé)
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Candidature non trouvée")
    
    # Supprime aussi le job associé
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    db.delete(application)
    if job:
        db.delete(job)
    
    db.commit()
    
    return {"message": "Candidature supprimée"}

@router.get("/stats/overview")
def get_stats(db: Session = Depends(get_db)):
    """
    Statistiques globales sur les candidatures
    """
    total = db.query(Application).count()
    
    by_status = {}
    statuses = ["draft", "applied", "interview", "rejected", "offer"]
    
    for status in statuses:
        count = db.query(Application).filter(Application.status == status).count()
        by_status[status] = count
    
    # Score moyen
    apps_with_score = db.query(Application).filter(Application.match_score.isnot(None)).all()
    avg_score = sum(app.match_score for app in apps_with_score) / len(apps_with_score) if apps_with_score else 0
    
    # Candidatures récentes (7 derniers jours)
    from datetime import timedelta
    recent = db.query(Application).filter(
        Application.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return {
        "total": total,
        "by_status": by_status,
        "average_match_score": round(avg_score, 1) if avg_score else None,
        "recent_applications": recent
    }

@router.get("/analytics/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    """
    Statistiques complètes pour le dashboard
    """
    return Analytics.get_dashboard_stats(db)