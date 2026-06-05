# Traffic E-Challan System - AI-Powered

An intelligent, autonomous traffic violation detection and management system utilizing Computer Vision (YOLOv8), OCR, and a completely localized, **RAG-powered AI Analytics engine**.

## 🚀 Features

- **Computer Vision**: YOLOv8-based detection of helmet and red-light violations.
- **OCR**: Automatic license plate extraction using EasyOCR.
- **Dashboard**: Real-time monitoring with a perfectly integrated React UI.
- **Local RAG AI Assistant**: Natural language querying, legal explanation generation, and automated reporting powered by a **Local LLM (Ollama)** and **ChromaDB**.
- **Advanced Analytics**: Scikit-Learn based predictive forecasting and high-risk hotspot clustering.
- **Enterprise Infrastructure**: Integrated Redis caching, Flask-Limiter rate limiting, and Celery background task processing.
- **Database Migrations**: Fully tracked database schema using `Flask-Migrate` (Alembic).

## ⚡ Quick Start (Recommended)

The entire backend infrastructure is Dockerized.

### Prerequisites
- [Docker & Docker Compose](https://www.docker.com/)
- [Ollama](https://ollama.com/) (For local AI features)
- Node.js 18+ (For frontend)

### 1. Start the Backend Infrastructure

```bash
# Spins up Flask, Redis, and the Celery worker
docker-compose up --build
```

### 2. Configure Local AI
To utilize the AI features, ensure Ollama is running on your host machine and pull the LLM:
```bash
ollama run llama3
```

### 3. Start the Frontend Dashboard
```bash
cd frontend
npm install
npm run dev             
```
Navigate to http://localhost:5173

---

## 🛠️ Manual Backend Setup (Without Docker)

```bash
cd backend
python -m venv venv


pip install -r requirements.txt


flask db upgrade
python seed_data.py


python scripts/ingest_data.py


python app.py
```
*(Note: To use caching and async tasks natively without Docker, you must run a Redis server on `localhost:6379` and spin up a celery worker: `celery -A tasks.tasks.celery_app worker`)*

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/violations` | Fetch all violations (paginated) |
| GET | `/api/violations/filter` | Filter by type, date, vehicle |
| POST | `/api/violation` | Create new violation |
| POST | `/api/ai/query` | Ask natural language questions via Local RAG |
| POST | `/api/ai/explain/:id` | Get AI legal explanations for a violation |
| GET | `/api/analytics/report` | Fetch cached automated daily summaries |
| GET | `/api/analytics/hotspots` | Fetch high-risk clustered locations |
| GET | `/api/analytics/forecast` | Fetch 7-day predictive violation forecasts |
| POST | `/api/cv/process-video` | Upload and process CCTV video |

## 🧠 Tech Stack

- **Backend**: Flask, SQLAlchemy, Alembic
- **AI & RAG**: LangChain, ChromaDB, HuggingFace (`all-MiniLM-L6-v2`), Ollama
- **Infrastructure**: Redis, Celery, Docker, Flask-Limiter
- **Frontend**: React 18, Vite, Recharts, TailwindCSS
- **CV**: YOLOv8 (ultralytics), OpenCV, EasyOCR

## ⚙️ Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:
- `LOCAL_LLM_MODEL`: e.g. `llama3` (defaults to llama3)
- `VECTOR_DB_PATH`: `./chroma_db`
- `REDIS_URL`: `redis://localhost:6379/0`
- `CELERY_BROKER_URL`: `redis://localhost:6379/0`
