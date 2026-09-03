# SkillgineX 🚀

**An AI-powered ATS Resume Analyzer using Multi-Agent LLMs & Hybrid RAG**

Optimize your resume for Applicant Tracking Systems (ATS) with intelligent, evidence-backed feedback. Upload your resume, paste a job description, and get instant insights on skill matches, gaps, and AI-tailored bullet points.

---

## ✨ Features

- **Smart Resume Analysis**: Multi-agent AI system evaluates your resume against job descriptions
- **Hybrid Search**: Combines keyword matching (BM25) + semantic search (Chroma embeddings) for accuracy
- **Real-Time ATS Score**: Match percentage with color-coded feedback (🟢 Good, 🟡 Fair, 🔴 Needs Work)
- **Skill Audit**: Itemized breakdown of matched, partial, and missing skills with evidence
- **AI Bullet Tailoring**: Generates resume bullets using Google's proven XYZ formula
- **Evidence Transparency**: View exact resume text chunks used in the analysis
- **Privacy-First**: Runs entirely locally with Ollama—no cloud data sharing
- **Modern Stack**: Full-stack decoupled architecture (FastAPI + Next.js)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Next.js Frontend (TypeScript)           │
│         ┌──────────────────────────────────────┐         │
│         │  Dashboard                            │         │
│         │  • Upload Resume (PDF)                │         │
│         │  • Paste Job Description              │         │
│         │  • View ATS Match Score               │         │
│         │  • Filter Skills (Found/Missing)      │         │
│         │  • Auto-Tailor Bullets                │         │
│         └──────────────────────────────────────┘         │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP (FormData / JSON)
                 ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│  ┌────────────────────────────────────────────────┐     │
│  │  Multi-Agent Orchestration                      │     │
│  │  1. PDF Extraction & Chunking                   │     │
│  │  2. Job Description Parsing (Agent 1)           │     │
│  │  3. Hybrid RAG Retrieval (BM25 + Chroma)        │     │
│  │  4. Skill Audit & Synthesis (Agent 2)           │     │
│  │  5. Guardrail Validation                        │     │
│  └────────────────────────────────────────────────┘     │
└────────────────┬────────────────────────────────────────┘
                 │ Local LLM
                 ↓
         ┌───────────────┐
         │ Ollama        │
         │ qwen3:0.6b    │
         └───────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **Ollama** with models: `qwen3:0.6b` and `qwen3-embedding:0.6b`

### 1. Install Ollama & Download Models

```bash
# Download Ollama from: https://ollama.ai
ollama serve

# In a new terminal, pull required models:
ollama pull qwen3:0.6b
ollama pull qwen3-embedding:0.6b
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python run.py
# OR manually:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 4. Test It Out

1. Go to `http://localhost:3000`
2. Upload a resume (PDF)
3. Select a sample job description or paste your own
4. Click **"Run ATS Audit"**
5. View your match score, skill audit, and AI recommendations

---

## 📁 Project Structure

```
SkillgineX/
├── backend/                              # FastAPI Application
│   ├── app/
│   │   ├── main.py                      # FastAPI entrypoint
│   │   ├── core/config.py               # Configuration & env variables
│   │   ├── schemas/ats.py               # Pydantic data models
│   │   ├── services/
│   │   │   ├── pdf_service.py           # PDF extraction & chunking
│   │   │   ├── rag_service.py           # Hybrid RAG (BM25 + Chroma)
│   │   │   └── agent_service.py         # Multi-agent LLM orchestration
│   │   └── api/endpoints/analyze.py     # API routes
│   ├── requirements.txt                  # Python dependencies
│   ├── run.py                           # Startup script
│   └── README.md                        # Detailed backend docs
│
├── frontend/                             # Next.js Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx               # Root layout
│   │   │   ├── page.tsx                 # Main dashboard
│   │   │   └── globals.css              # Tailwind styling
│   │   ├── components/
│   │   │   ├── Navbar.tsx               # Header with health check
│   │   │   ├── ScoreGauge.tsx           # ATS match score ring
│   │   │   ├── SkillMatrix.tsx          # Skill audit table
│   │   │   ├── BulletTailorerModal.tsx  # AI bullet generator
│   │   │   └── RetrievedEvidenceModal.tsx # RAG transparency
│   │   ├── types/ats.ts                 # TypeScript interfaces
│   │   └── data/jobPresets.ts           # Sample job descriptions
│   ├── package.json                     # Dependencies
│   ├── next.config.js                   # Next.js configuration
│   └── README.md                        # Detailed frontend docs
│
└── README.md                            # This file
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/` | Service status and links |
| `GET` | `/api/v1/health` | Health check & Ollama connectivity |
| `POST` | `/api/v1/analyze` | Analyze resume against job description |
| `POST` | `/api/v1/tailor-bullets` | Generate XYZ formula bullets |
| `GET` | `/docs` | Interactive Swagger API documentation |

### Example: Analyze Resume

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "resume=@resume.pdf" \
  -F "job_description=Software Engineer with 5+ years Python experience..."
```

**Response:**
```json
{
  "match_percentage": 85,
  "summary_verdict": "Strong match",
  "strengths": ["Python expertise", "FastAPI experience"],
  "critical_gaps": ["Kubernetes experience"],
  "skill_audit": [
    {
      "skill": "Python",
      "status": "FOUND",
      "evidence": "Expert in Python 3.10+, built multiple FastAPI services"
    }
  ],
  "recommendations": ["Learn Kubernetes basics"],
  "retrieved_chunks": [...]
}
```

---

## 🧠 How It Works

### The Resume Analysis Pipeline

1. **PDF Extraction** → Resume text is extracted and split into semantic sections (Summary, Experience, Skills, Projects)
2. **JD Parsing** → AI Agent 1 extracts structured requirements from the job description
3. **Hybrid Search** → Resume sections are searched using:
   - **BM25**: Exact keyword matching (Python, AWS, etc.)
   - **Chroma**: Semantic similarity (AI finds "machine learning" when you write "deep learning")
4. **Skill Audit** → AI Agent 2 evaluates each skill from the JD against retrieved resume evidence
5. **Guardrails** → JSON validation ensures output quality; LLM self-corrects on failures
6. **Score Generation** → Match percentage and itemized feedback returned

### Why Hybrid RAG?

- **BM25 (Sparse)**: Perfect for technical terms and acronyms that must be exact
- **Chroma (Dense)**: Catches semantic meaning when wording differs
- **Together**: More accurate and contextually rich than either alone

---

## 💡 Key Technologies

### Backend
- **FastAPI** — Async Python web framework
- **PyPDF** — PDF text extraction
- **LangChain** — LLM orchestration
- **Chroma** — Vector embeddings & search
- **Rank-BM25** — Keyword search algorithm
- **Pydantic** — Data validation & schemas
- **Ollama** — Local LLM inference

### Frontend
- **Next.js 14** (App Router) — React framework
- **TypeScript** — Type-safe development
- **Tailwind CSS** — Utility-first styling
- **React Hooks** — State management

---

## 🛠️ Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### Environment Variables

**Backend** (`.env` in `backend/`):
```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen3:0.6b
EMBEDDING_MODEL=qwen3-embedding:0.6b
FRONTEND_URL=http://localhost:3000
```

**Frontend** (`.env.local` in `frontend/`):
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 📊 Tech Stack Summary

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| Frontend | Next.js + TypeScript + Tailwind | Modern, type-safe UI |
| Backend | FastAPI + Python | High-performance async API |
| AI/ML | Ollama + LangChain | Local LLM inference & orchestration |
| Search | BM25 + Chroma | Hybrid semantic/keyword retrieval |
| Data | Pydantic | Type validation & contracts |
| Styling | Tailwind CSS v4 | Responsive design |

---

## 🎯 Use Cases

- **Job Seekers**: Optimize resumes before applying to jobs
- **Career Coaches**: Help clients understand ATS requirements
- **Recruiters**: Benchmark resume quality objectively
- **Engineering Teams**: Develop internal talent assessment tools

---

## 🚀 Future Enhancements

- [ ] Multi-resume bulk analysis
- [ ] Resume template suggestions
- [ ] Industry-specific benchmarking
- [ ] Cover letter optimization
- [ ] Job market insights & salary data
- [ ] Integration with LinkedIn
- [ ] Cloud deployment (AWS/GCP)

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🙋 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

## 📧 Contact

Built by **@ShresthaGupta**  
Questions or feedback? [Open an issue](https://github.com/ShresthaGupta/SkillgineX/issues)

---

## 🙏 Acknowledgments

- Inspired by modern ATS evaluation practices
- Built with [Ollama](https://ollama.ai) for local LLM inference
- Powered by [LangChain](https://langchain.com) for multi-agent orchestration
- UI built with [Tailwind CSS](https://tailwindcss.com)

---

**Happy optimizing! 🎉**
