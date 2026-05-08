# backend/main.py
import sys
import os
import locale

# Force UTF-8 encoding AVANT tout
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

# Set default encoding
if sys.version_info >= (3, 7):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass

# Maintenant les imports normaux
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import engine, Base
from api import jobs, cvs, cover_letters, applications, interview_prep

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job AI Assistant API",
    description="API pour assistant IA de candidature",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "🚀 Job AI Assistant API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(cvs.router, prefix="/api/cvs", tags=["cvs"])
app.include_router(cover_letters.router, prefix="/api/cover-letters", tags=["cover-letters"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])  # ← NOUVEAU
app.include_router(interview_prep.router, prefix="/api/interview-prep", tags=["interview-prep"])  # ← NOUVEAU

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)