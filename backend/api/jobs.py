# backend/api/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from models.database import get_db
from models.models import Job, Application, UserCV
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
        
        # Analyse avec Gemini
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
        
        print(f"✅ Job enregistré avec ID: {db_job.id}")
        
        # Crée automatiquement une application en draft
        db_application = Application(
            job_id=db_job.id,
            status="draft"
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        print(f"✅ Application créée avec ID: {db_application.id}")
        
        # ===== CALCUL DU MATCH SCORE =====
        match_result = None
        match_score_value = None
        
        print(f"🔍 Recherche d'un CV actif...")
        
        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        
        if cv:
            print(f"✅ CV actif trouvé : {cv.filename} (ID: {cv.id})")
            
            try:
                print(f"🎯 Calcul du match score en cours...")
                
                # Import CVParser
                from services.cv_parser import CVParser
                cv_parser = CVParser()
                
                # Crée le profil utilisateur
                user_profile = cv_parser.create_user_profile(cv.parsed_data)
                print(f"✅ Profil utilisateur créé")
                
                # Calcule le match
                match_result = analyzer.calculate_match_score(analysis, user_profile)
                match_score_value = match_result["score"]
                
                print(f"✅ Match score calculé : {match_score_value}/100")
                
                # Sauvegarde le score dans l'application
                db_application.match_score = match_score_value
                db.commit()
                db.refresh(db_application)
                
                print(f"✅ Score sauvegardé dans l'application")
                
            except Exception as e:
                print(f"❌ Erreur lors du calcul du match score : {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️  Pas de CV actif trouvé, match score non calculé")
            
            # Debug : liste tous les CVs
            all_cvs = db.query(UserCV).all()
            print(f"📋 CVs dans la base : {len(all_cvs)}")
            for c in all_cvs:
                print(f"   - CV {c.id}: {c.filename}, is_active={c.is_active}")
        
        # ===== RETOUR =====
        return {
            "job_id": db_job.id,
            "application_id": db_application.id,
            "analysis": analysis,
            "match_score": match_score_value,
            "match_details": match_result,
            "message": "Offre analysée et enregistrée avec succès"
        }
        
    except Exception as e:
        print(f"❌ Erreur globale : {str(e)}")
        import traceback
        traceback.print_exc()
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


@router.post("/recalculate-all-scores")
def recalculate_all_scores(db: Session = Depends(get_db)):
    """
    Recalcule les match scores pour toutes les candidatures
    (Utilisé après upload d'un nouveau CV)
    """
    try:
        # Récupère le CV actif
        from models.models import UserCV
        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        if not cv:
            raise HTTPException(status_code=400, detail="Aucun CV actif")
        
        from services.cv_parser import CVParser
        cv_parser = CVParser()
        user_profile = cv_parser.create_user_profile(cv.parsed_data)
        
        # Récupère toutes les applications
        applications = db.query(Application).all()
        
        updated_count = 0
        results = []
        
        for app in applications:
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if job:
                print(f"🎯 Calcul score pour : {job.title}")
                
                match_result = analyzer.calculate_match_score(
                    job.requirements,
                    user_profile
                )
                
                app.match_score = match_result["score"]
                updated_count += 1
                
                results.append({
                    "job_id": job.id,
                    "title": job.title,
                    "new_score": match_result["score"]
                })
        
        db.commit()
        
        print(f"✅ {updated_count} scores recalculés")
        
        return {
            "message": f"{updated_count} candidatures mises à jour",
            "updated_count": updated_count,
            "results": results
        }
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))