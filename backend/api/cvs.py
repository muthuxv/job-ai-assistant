# backend/api/cvs.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from datetime import datetime

from models.database import get_db
from models.models import UserCV, Application, UserSettings
from services.cv_parser import CVParser
from services.llm_provider import get_provider, BaseLLMProvider

router = APIRouter()

UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_llm_provider(db: Session = Depends(get_db)) -> BaseLLMProvider:
    settings = db.query(UserSettings).first()
    if settings and settings.api_key:
        return get_provider(settings.provider, settings.api_key)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=400, detail="Aucun provider configuré.")
    return get_provider("gemini", gemini_key)


@router.post("/upload", response_model=dict)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider)
):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Seuls les PDFs sont acceptés")

        print(f"📤 Upload du CV : {file.filename}")

        file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cv_parser = CVParser(provider)
        cv_text = cv_parser.extract_text_from_pdf(file_path)

        print(f"🧠 Analyse avec {provider.__class__.__name__}...")
        parsed_data = cv_parser.parse_cv(cv_text)
        print(f"✅ CV parsé : {parsed_data['personal_info']['name']}")

        db.query(UserCV).update({"is_active": 0})

        db_cv = UserCV(
            filename=file.filename,
            content=cv_text,
            parsed_data=parsed_data,
            is_active=1
        )
        db.add(db_cv)
        db.commit()
        db.refresh(db_cv)

        applications_count = db.query(Application).count()
        applications_without_score = db.query(Application).filter(
            Application.match_score.is_(None)
        ).count()

        return {
            "cv_id": db_cv.id,
            "parsed_data": parsed_data,
            "message": "CV uploadé et analysé avec succès",
            "total_applications": applications_count,
            "applications_without_score": applications_without_score
        }

    except Exception as e:
        print(f"❌ Erreur upload CV : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
def get_active_cv(db: Session = Depends(get_db)):
    return db.query(UserCV).filter(UserCV.is_active == 1).first()


@router.get("/")
def get_all_cvs(db: Session = Depends(get_db)):
    return db.query(UserCV).order_by(UserCV.created_at.desc()).all()


@router.get("/{cv_id}")
def get_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(UserCV).filter(UserCV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV non trouvé")
    return cv


@router.delete("/{cv_id}")
def delete_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(UserCV).filter(UserCV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV non trouvé")
    db.delete(cv)
    db.commit()
    return {"message": "CV supprimé"}