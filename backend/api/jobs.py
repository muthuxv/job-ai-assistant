# backend/api/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

from models.database import get_db
from models.models import Job, Application, UserCV, UserSettings
from services.job_analyzer import JobAnalyzer
from services.cv_parser import CVParser
from services.llm_provider import get_provider, BaseLLMProvider

router = APIRouter()

# ── Provider injection ──────────────────────────────────────────
def get_llm_provider(db: Session = Depends(get_db)) -> BaseLLMProvider:
    settings = db.query(UserSettings).first()
    if settings and settings.api_key:
        return get_provider(settings.provider, settings.api_key)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=400, detail="Aucun provider configuré. Allez dans Paramètres.")
    return get_provider("gemini", gemini_key)

# ── Pydantic models ─────────────────────────────────────────────
class JobCreate(BaseModel):
    description: str
    url: Optional[str] = None

class MatchRequest(BaseModel):
    job_id: int
    user_profile: dict

# ── Endpoints ───────────────────────────────────────────────────
@router.post("/analyze", response_model=dict)
def analyze_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider)
):
    try:
        analyzer = JobAnalyzer(provider)

        print(f"📊 Analyse de l'offre en cours...")
        analysis = analyzer.analyze_job(job.description)
        print(f"✅ Analyse terminée : {analysis['title']} chez {analysis['company']}")

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

        db_application = Application(job_id=db_job.id, status="draft")
        db.add(db_application)
        db.commit()
        db.refresh(db_application)

        # Match score auto si CV actif
        match_result = None
        match_score_value = None

        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        if cv:
            try:
                print(f"🎯 Calcul du match score...")
                cv_parser = CVParser(provider)
                user_profile = cv_parser.create_user_profile(cv.parsed_data)
                match_result = analyzer.calculate_match_score(analysis, user_profile)
                match_score_value = match_result["score"]

                db_application.match_score = match_score_value
                db_application.match_details = match_result
                db.commit()
                db.refresh(db_application)
                print(f"✅ Match score : {match_score_value}/100")
            except Exception as e:
                print(f"❌ Erreur match score : {str(e)}")
        else:
            print(f"⚠️  Pas de CV actif")

        return {
            "job_id": db_job.id,
            "application_id": db_application.id,
            "analysis": analysis,
            "match_score": match_score_value,
            "match_details": match_result,
            "message": "Offre analysée et enregistrée avec succès"
        }

    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[dict])
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "url": j.url,
            "created_at": j.created_at
        }
        for j in jobs
    ]


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return job


@router.post("/match")
def calculate_match(
    match_req: MatchRequest,
    db: Session = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider)
):
    try:
        job = db.query(Job).filter(Job.id == match_req.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Offre non trouvée")

        analyzer = JobAnalyzer(provider)
        match_result = analyzer.calculate_match_score(job.requirements, match_req.user_profile)

        application = db.query(Application).filter(Application.job_id == match_req.job_id).first()
        if application:
            application.match_score = match_result["score"]
            application.match_details = match_result
            db.commit()

        return {"job_id": match_req.job_id, "match_result": match_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recalculate-all-scores")
def recalculate_all_scores(
    db: Session = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider)
):
    try:
        cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
        if not cv:
            raise HTTPException(status_code=400, detail="Aucun CV actif")

        cv_parser = CVParser(provider)
        analyzer = JobAnalyzer(provider)
        user_profile = cv_parser.create_user_profile(cv.parsed_data)

        applications = db.query(Application).all()
        updated_count = 0
        results = []

        for app in applications:
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if job:
                match_result = analyzer.calculate_match_score(job.requirements, user_profile)
                app.match_score = match_result["score"]
                app.match_details = match_result
                updated_count += 1
                results.append({
                    "job_id": job.id,
                    "title": job.title,
                    "new_score": match_result["score"]
                })

        db.commit()
        return {
            "message": f"{updated_count} candidatures mises à jour",
            "updated_count": updated_count,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    db.delete(job)
    db.commit()
    return {"message": "Offre supprimée"}