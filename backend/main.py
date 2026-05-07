# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import engine, Base
from api import jobs, cvs, cover_letters

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
        "docs": "/docs"
    }

# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(cvs.router, prefix="/api/cvs", tags=["cvs"])  # ← NOUVEAU
app.include_router(cover_letters.router, prefix="/api/cover-letters", tags=["cover-letters"])  # ← NOUVEAU

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)