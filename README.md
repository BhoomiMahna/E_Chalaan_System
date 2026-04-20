# Traffic E-Challan System - AI-Powered

An intelligent traffic violation detection and management system using Computer Vision (YOLOv8), OCR, and AI-powered analytics.

## Features

- **Computer Vision**: YOLOv8-based detection of helmet and red-light violations
- **OCR**: Automatic license plate extraction using EasyOCR
- **Dashboard**: Real-time monitoring with charts and statistics
- **AI Assistant**: Natural language queries, violation explanations, and predictive analytics
- **Database**: SQLite (dev) / PostgreSQL (production) with SQLAlchemy ORM

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python seed_data.py      # Seed 250 demo violations
python app.py            # Start Flask on port 5000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev              # Start Vite on port 5173
```

### Open Dashboard
Navigate to http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/violations | Fetch all violations (paginated) |
| GET | /api/violations/filter | Filter by type, date, vehicle |
| POST | /api/violation | Create new violation |
| GET | /api/stats | Dashboard statistics |
| POST | /api/ai/query | Natural language query |
| POST | /api/ai/explain/:id | AI explanation for violation |
| GET | /api/ai/predict | Predictive analytics |
| POST | /api/cv/process-video | Upload and process video |
| POST | /api/cv/start-webcam | Start webcam processing |
| GET | /api/health | Health check |

## AI Features

1. **Query Agent**: Ask questions like "Show helmet violations today" or "Total fines this week"
2. **Explanation Generator**: Get detailed AI-powered explanations for any violation
3. **Prediction Model**: View high-risk areas, peak hours, and 7-day forecasts

## Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: React 18, Vite, Recharts, Lucide Icons
- **CV**: YOLOv8 (ultralytics), OpenCV, EasyOCR
- **AI**: Google Gemini API, scikit-learn

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:
- `GEMINI_API_KEY`: Google Gemini API key (optional, enables AI features)
- `DATABASE_URL`: Database connection string (defaults to SQLite)

## Optional: Install CV Dependencies

```bash
pip install ultralytics opencv-python easyocr
```
