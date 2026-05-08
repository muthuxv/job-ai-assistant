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

---

## 🛠️ Tech Stack

### Backend
| Tech | Usage |
|------|-------|
| **FastAPI** | REST API with auto-generated Swagger docs |
| **SQLAlchemy** | ORM with PostgreSQL / SQLite |
| **Google Gemini** | LLM for analysis, generation and embeddings |
| **Anthropic Claude** | Writing quality for cover letters |
| **LangChain** | LLM orchestration framework |
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
│   Dashboard · New Application · CV Upload · Detail      │
└────────────────────────┬────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                        │
├──────────────┬──────────────┬─────────────┬─────────────┤
│ Job Analyzer │  CV Parser   │Cover Letter │Interview    │
│              │              │ Generator   │  Preparer   │
└──────────────┴──────────────┴─────────────┴─────────────┘
        │               │              │
        ▼               ▼              ▼
   ┌─────────┐    ┌──────────┐   ┌──────────┐
   │ Gemini  │    │PostgreSQL│   │  Claude  │
   │   API   │    │    DB    │   │   API    │
   └─────────┘    └──────────┘   └──────────┘
```

---

## 🔄 How It Works

### Job Analysis Flow
```
Paste job posting
      ↓
Gemini extracts → title, company, skills, ATS keywords,
                  responsibilities, salary, benefits
      ↓
If CV uploaded → Match Score calculated automatically
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
- Google Gemini API key → [Get one here](https://makersuite.google.com/app/apikey)
- Anthropic Claude API key → [Get one here](https://console.anthropic.com)

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
# Edit .env and add your API keys
```

**.env file:**
```env
DATABASE_URL=sqlite:///./job_assistant.db
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Run the app

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

---

## 📱 Usage

### Step 1 — Upload your CV
Go to **Mon CV** and upload your PDF. LaunchPad extracts your full profile automatically.

### Step 2 — Analyse a job posting
Click **Nouvelle candidature**, paste the job description and let the AI work.  
You'll instantly see:
- Extracted skills and ATS keywords
- Your compatibility score (0–100)
- Strengths, gaps and recommendations

### Step 3 — Generate your cover letter
Open the application detail and click **Générer 3 versions**.  
Switch between Formal, Startup and Tech tones — copy the best one.

### Step 4 — Prepare your interview
Click **Générer la préparation** to get:
- General questions with suggested answers
- Technical questions by topic
- Behavioural questions with STAR examples
- Smart questions to ask the recruiter

### Step 5 — Track your applications
Update statuses as you progress: **Draft → Applied → Interview → Offer / Rejected**

---

## 📁 Project Structure

```
launchpad/
├── backend/
│   ├── api/
│   │   ├── jobs.py              # Job analysis endpoints
│   │   ├── cvs.py               # CV upload endpoints
│   │   ├── applications.py      # Application tracking
│   │   ├── cover_letters.py     # Cover letter generation
│   │   └── interview_prep.py    # Interview preparation
│   ├── models/
│   │   ├── database.py          # SQLAlchemy setup
│   │   └── models.py            # DB models (Job, Application, CV, CoverLetter)
│   ├── services/
│   │   ├── job_analyzer.py      # LLM job analysis + match scoring
│   │   ├── cv_parser.py         # PDF extraction + CV parsing
│   │   ├── cover_letter_generator.py  # Multi-tone generation
│   │   ├── interview_prep.py    # Question generation
│   │   └── analytics.py        # Dashboard stats
│   ├── main.py                  # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # GlassCard, NeonButton, StatusBadge...
│   │   ├── pages/               # Dashboard, NewApplication, Detail, UploadCV
│   │   └── services/
│   │       └── api.js           # API service layer
│   └── package.json
├── .env.example
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
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

Full interactive docs available at `http://localhost:8000/docs`

---

## 🧠 Key Technical Decisions

**Why RAG-inspired architecture instead of fine-tuning?**  
Job postings and CVs change constantly. Fine-tuning is expensive and rigid. The LLM Judge approach (passing structured context at inference time) is flexible, updatable and traceable.

**Why Gemini for analysis + Claude for writing?**  
Gemini Flash is fast and cost-effective for structured extraction and JSON output. Claude produces noticeably more natural prose for cover letters — the two complement each other well.

**Why persist match_details in the database?**  
Match scores are only useful if you can review the reasoning later. Storing the full breakdown (strengths, gaps, recommendations) means insights are available every time you open an application.

**Why optional CV upload (not mandatory)?**  
Forcing CV upload before exploring breaks the flow. Users can analyse jobs first, then upload their CV and trigger score recalculation — reducing friction without sacrificing functionality.

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
