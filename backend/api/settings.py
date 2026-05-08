# backend/api/settings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os

from models.database import get_db
from models.models import UserSettings
from services.llm_provider import get_provider, BaseLLMProvider  # ← AJOUTE BaseLLMProvider

router = APIRouter()

PROVIDER_MODELS = {
    "gemini": {
        "name": "Google Gemini",
        "models": ["gemini-3-flash-preview, gemini-3.1-flash-lite"],
        "default_model": "gemini-3.1-flash-lite",
        "docs_url": "https://makersuite.google.com/app/apikey",
        "free_tier": True
    },
    "claude": {
        "name": "Anthropic Claude",
        "models": ["claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"],
        "default_model": "claude-sonnet-4-20250514",
        "docs_url": "https://console.anthropic.com",
        "free_tier": False
    },
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o-mini", "gpt-4o"],
        "default_model": "gpt-4o-mini",
        "docs_url": "https://platform.openai.com/api-keys",
        "free_tier": False
    }
}

class SettingsUpdate(BaseModel):
    provider: str
    api_key: str
    model_name: Optional[str] = None

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    """Récupère les settings actuels"""
    settings = db.query(UserSettings).first()
    
    if not settings:
        return {
            "provider": "gemini",
            "model_name": "gemini-3-flash-preview",
            "api_key_set": False,
            "providers_info": PROVIDER_MODELS
        }
    
    return {
        "provider": settings.provider,
        "model_name": settings.model_name,
        "api_key_set": bool(settings.api_key),
        "providers_info": PROVIDER_MODELS
    }

@router.post("/")
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db)):
    """Met à jour le provider et la clé API"""
    
    if data.provider not in PROVIDER_MODELS:
        raise HTTPException(status_code=400, detail=f"Provider inconnu : {data.provider}")
    
    # Test avec un prompt plus neutre
    print(f"🔑 Test de la clé API {data.provider}...")
    try:
        provider = get_provider(data.provider, data.api_key)
        test_response = provider.generate(
            "What is 2 + 2? Reply with just the number.",
            temperature=0,
            max_tokens=10
        )
        print(f"✅ Clé API valide, test response : {test_response}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Clé API invalide : {str(e)}")
    
    # Sauvegarde
    settings = db.query(UserSettings).first()
    
    if settings:
        settings.provider = data.provider
        settings.api_key = data.api_key
        settings.model_name = data.model_name or PROVIDER_MODELS[data.provider]["default_model"]
    else:
        settings = UserSettings(
            provider=data.provider,
            api_key=data.api_key,
            model_name=data.model_name or PROVIDER_MODELS[data.provider]["default_model"]
        )
        db.add(settings)
    
    db.commit()
    
    return {
        "message": f"✅ Provider {data.provider} configuré avec succès",
        "provider": data.provider,
        "model": settings.model_name
    }