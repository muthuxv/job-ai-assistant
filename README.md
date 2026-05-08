# 🚀 LaunchPad — AI-powered Job Application Assistant

> **Give yourself an unfair advantage.**  
> LaunchPad uses AI to analyse job postings, match them against your CV, generate personalised cover letters and prepare you for interviews — all in one place.

![LaunchPad Dashboard](screenshots/dashboard.png)

---

## ✨ Features

- **🔍 Job Analysis** — Paste any job posting and get instant structured extraction: required skills, ATS keywords, responsibilities, salary range
- **🎯 Match Score** — AI calculates your CV-to-job compatibility with detailed strengths, gaps and actionable recommendations
- **✉️ Cover Letter Generation** — 3 personalised versions in different tones (Formal, Startup, Tech) via advanced prompt engineering
- **🎤 Interview Preparation** — Likely questions (general, technical, behavioural), STAR framework tips, and questions to ask the recruiter
- **📊 Application Tracker** — Dashboard to manage all your applications with status tracking (Draft → Applied → Interview → Offer)
- **📄 CV Parsing** — Upload your CV once, AI extracts your full profile for automatic personalisation
- **🔌 Multi-provider LLM** — Choose your preferred AI provider: Google Gemini, Anthropic Claude or OpenAI GPT

---

## 🛠️ Tech Stack

### Backend
| Tech | Usage |
|------|-------|
| **FastAPI** | REST API with auto-generated Swagger docs |
| **SQLAlchemy** | ORM with PostgreSQL / SQLite |
| **LLM Provider Layer** | Abstraction over Gemini, Claude and OpenAI |
| **Google Gemini** | Default LLM — fast, cost-effective, generous free tier |
| **Anthropic Claude** | Optional — best for nuanced writing |
| **OpenAI GPT** | Optional — reliable, versatile |
| **PyPDF** | CV text extraction |

### Frontend
| Tech | Usage |
|------|-------|
| **React 18** | UI framework |
| **Tailwind CSS v3** | Styling |
| **Framer Motion** | Animations |
| **Recharts** | Analytics charts |
| **Axios** | HTTP client |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   React Frontend                         │
│  Dashboard · New Application · CV Upload · Settings     │
└────────────────────────┬────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                        │
├──────────────┬──────────────┬─────────────┬─────────────┤
│ Job Analyzer │  CV Parser   │Cover Letter │Interview    │
│              │              │ Generator   │  Preparer   │
└──────────────┴──────────────┴─────────────┴─────────────┘
                       │
          ┌────────────▼────────────┐
          │   LLM Provider Layer    │
          │  (provider abstraction) │
          └────────┬────────────────┘
         ┌─────────┼──────────┐
         ▼         ▼          ▼
     ┌───────┐ ┌───────┐ ┌────────┐
     │Gemini │ │Claude │ │OpenAI  │
     └───────┘ └───────┘ └────────┘
                    │
             ┌──────▼──────┐
             │ PostgreSQL  │
             │     DB      │
             └─────────────┘
```

---

## 🔌 Multi-provider LLM Support

LaunchPad uses a **provider abstraction layer** that decouples all AI services from any specific LLM vendor. Every service (`JobAnalyzer`, `CVParser`, `CoverLetterGenerator`, `InterviewPreparer`) receives a provider instance at runtime — switching models requires zero code changes.

```python
# All services follow the same pattern
class JobAnalyzer:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider  # Gemini, Claude or OpenAI

    def analyze_job(self, description: str) -> dict:
        return self.provider.generate_json(prompt)  # Same call, any provider
```

Configure your preferred provider in the **Settings** page — your API key is validated before saving and stored locally.

| Provider | Model | Free tier | Best for |
|----------|-------|-----------|----------|
| **Google Gemini** | gemini-3.1-flash-lite-preview | ✅ Yes | Default, fast, cost-effective |
| **Anthropic Claude** | claude-sonnet-4 | ❌ No | Nuanced writing, cover letters |
| **OpenAI GPT** | gpt-4o-mini | ❌ No | Versatile, reliable |

---

## 🔄 How It Works

### Job Analysis Flow
```
Paste job posting
      ↓
LLM extracts → title, company, skills, ATS keywords,
               responsibilities, salary, benefits
      ↓
If CV uploaded → Match Score calculated automatically
      ↓
Match details persisted (strengths, gaps, recommendations)
      ↓
Application saved to dashboard
```

### Cover Letter Flow
```
Select application
      ↓
Choose tone (Formal / Startup / Tech)
      ↓
LLM generates personalised letter using:
  - Job requirements
  - Your CV profile
  - Advanced prompt engineering
      ↓
Copy & send
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- API key for at least one provider:
  - Google Gemini (free) → [Get one here](https://makersuite.google.com/app/apikey)
  - Anthropic Claude → [Get one here](https://console.anthropic.com)
  - OpenAI → [Get one here](https://platform.openai.com/api-keys)

### 1. Clone the repo

```bash
git clone https://github.com/muthuxv/launchpad.git
cd launchpad
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — only GEMINI_API_KEY is required as fallback
```

**.env file:**
```env
DATABASE_URL=sqlite:///./job_assistant.db
GEMINI_API_KEY=your_gemini_key_here
```

### 3. Database setup

```bash
python3 -c "
from models.database import engine, Base
from models.models import *
from sqlalchemy import text, inspect

Base.metadata.create_all(bind=engine)

inspector = inspect(engine)
existing = [col['name'] for col in inspector.get_columns('applications')]

with engine.connect() as conn:
    if 'match_details' not in existing:
        conn.execute(text('ALTER TABLE applications ADD COLUMN match_details JSON'))
    conn.commit()

print('Migration complete')
"
```

### 4. Frontend setup

```bash
cd frontend
npm install
```

### 5. Run the app

```bash
# Terminal 1 — Backend
cd backend
python main.py
# API running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs

# Terminal 2 — Frontend
cd frontend
npm start
# App running at http://localhost:3000
```

### 6. Configure your LLM provider

Go to **Paramètres** in the app, select your preferred provider and enter your API key.

---

## 📱 Usage

### Step 1 — Configure your provider
Go to **Paramètres**, choose Gemini, Claude or OpenAI and enter your API key.

### Step 2 — Upload your CV
Go to **Mon CV** and upload your PDF. LaunchPad extracts your full profile automatically.

### Step 3 — Analyse a job posting
Click **Nouvelle candidature**, paste the job description and let the AI work.

### Step 4 — Generate your cover letter
Open the application detail and click **Générer 3 versions**. Switch between Formal, Startup and Tech tones.

### Step 5 — Prepare your interview
Click **Générer la préparation** to get questions, STAR framework tips and smart questions to ask the recruiter.

### Step 6 — Track your applications
Update statuses: **Draft → Applied → Interview → Offer / Rejected**

---

## 📁 Project Structure

```
launchpad/
├── backend/
│   ├── api/
│   │   ├── jobs.py
│   │   ├── cvs.py
│   │   ├── applications.py
│   │   ├── cover_letters.py
│   │   ├── interview_prep.py
│   │   └── settings.py          # LLM provider configuration
│   ├── models/
│   │   ├── database.py
│   │   └── models.py            # Job, Application, CV, CoverLetter, UserSettings
│   ├── services/
│   │   ├── llm_provider.py      # Provider abstraction (Gemini, Claude, OpenAI)
│   │   ├── job_analyzer.py
│   │   ├── cv_parser.py
│   │   ├── cover_letter_generator.py
│   │   ├── interview_prep.py
│   │   └── analytics.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/               # Dashboard, NewApplication, Detail, UploadCV, Settings
│   │   └── services/api.js
│   └── package.json
├── .env.example
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/settings/` | Get current provider config |
| `POST` | `/api/settings/` | Update provider + API key |
| `POST` | `/api/jobs/analyze` | Analyse a job posting |
| `GET` | `/api/jobs/` | List all jobs |
| `POST` | `/api/jobs/recalculate-all-scores` | Recalculate match scores |
| `POST` | `/api/cvs/upload` | Upload and parse a CV |
| `GET` | `/api/cvs/active` | Get active CV |
| `GET` | `/api/applications/` | List all applications |
| `PATCH` | `/api/applications/{id}` | Update application status |
| `GET` | `/api/applications/analytics/dashboard` | Dashboard analytics |
| `POST` | `/api/cover-letters/generate` | Generate cover letter |
| `POST` | `/api/cover-letters/generate-all-tones` | Generate 3 versions |
| `GET` | `/api/interview-prep/{id}` | Generate interview prep |

Full interactive docs at `http://localhost:8000/docs`

---

## 🧠 Key Technical Decisions

**Why a provider abstraction layer?**  
Vendor lock-in is a real risk with LLM APIs. The `BaseLLMProvider` interface decouples all business logic from any specific provider. Switching from Gemini to Claude is a single settings change — zero code touched.

**Why RAG-inspired architecture instead of fine-tuning?**  
Job postings and CVs change constantly. Fine-tuning is expensive and rigid. The LLM Judge approach is flexible, updatable and traceable.

**Why persist match_details in the database?**  
Match scores are only useful if you can review the reasoning later. Storing the full breakdown means insights are available every time you open an application.

**Why optional CV upload?**  
Forcing CV upload before exploring breaks the flow. Users can analyse jobs first, upload their CV later and trigger score recalculation.

**Why Gemini as the default?**  
Generous free tier, fast response times and solid performance. The abstraction layer means users can switch to Claude or GPT-4o with one click.

---

## 🔮 Roadmap

- [ ] Streaming responses (letter generation word by word)
- [ ] Multi-document support (search across multiple CVs)
- [ ] LinkedIn job scraper (auto-import job postings)
- [ ] Response caching (avoid redundant API calls)
- [ ] Docker deployment
- [ ] Multi-user authentication
- [ ] Hybrid search (semantic + keyword)

---

## 📄 License

MIT

---

## 👤 Author

Full Stack Developer · Building AI-powered Products

- GitHub: [@muthuxv](https://github.com/muthuxv)
- Email: muthulan.m@gmail.com

---

*Built as part of an intensive AI learning sprint — from zero LLM knowledge to a full production-ready application in 4 weeks.*