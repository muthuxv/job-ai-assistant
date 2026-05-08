# backend/api/cvs.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from datetime import datetime

from models.database import get_db
from models.models import UserCV
from services.cv_parser import CVParser

router = APIRouter()
parser = CVParser()

UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class CVResponse(BaseModel):
    id: int
    filename: str
    parsed_data: dict
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/upload", response_model=dict)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload et parse un CV (PDF)
    """
    try:
        # Vérifie que c'est un PDF
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Seuls les PDFs sont acceptés")
        
        print(f"📤 Upload du CV : {file.filename}")
        
        # Sauvegarde le fichier
        file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Fichier sauvegardé : {file_path}")
        
        # Extrait le texte
        print(f"📄 Extraction du texte...")
        cv_text = parser.extract_text_from_pdf(file_path)
        
        # Parse avec Claude
        print(f"🧠 Analyse avec Claude...")
        parsed_data = parser.parse_cv(cv_text)
        
        print(f"✅ CV parsé : {parsed_data['personal_info']['name']}")
        
        # Désactive les anciens CVs
        db.query(UserCV).update({"is_active": 0})
        
        # Sauvegarde dans DB
        db_cv = UserCV(
            filename=file.filename,
            content=cv_text,
            parsed_data=parsed_data,
            is_active=1
        )
        db.add(db_cv)
        db.commit()
        db.refresh(db_cv)

        # Compte les candidatures existantes sans score
        from models.models import Application
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

@router.get("/active", response_model=Optional[CVResponse])
def get_active_cv(db: Session = Depends(get_db)):
    """
    Récupère le CV actif
    """
    cv = db.query(UserCV).filter(UserCV.is_active == 1).first()
    return cv

@router.get("/", response_model=list[CVResponse])
def get_all_cvs(db: Session = Depends(get_db)):
    """
    Récupère tous les CVs
    """
    cvs = db.query(UserCV).order_by(UserCV.created_at.desc()).all()
    return cvs

@router.get("/{cv_id}", response_model=CVResponse)
def get_cv(cv_id: int, db: Session = Depends(get_db)):
    """
    Récupère un CV spécifique
    """
    cv = db.query(UserCV).filter(UserCV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV non trouvé")
    return cv

@router.delete("/{cv_id}")
def delete_cv(cv_id: int, db: Session = Depends(get_db)):
    """
    Supprime un CV
    """
    cv = db.query(UserCV).filter(UserCV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV non trouvé")
    
    db.delete(cv)
    db.commit()
    
    return {"message": "CV supprimé"}