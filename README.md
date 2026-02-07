# Clinical Trial Search

**Discover clinical trials that match—not the other way around.**

A natural-language search app for clinical trials. Type a query in plain English (e.g. *"Phase 2 breast cancer trials with BRCA1"*), and get results plus an AI-generated summary. Built with Elasticsearch, FastAPI, React, and optional OpenAI for spell correction and summaries.

---

## Features

- **Natural language search** — Parse queries like "Phase 2 recruiting trials for Alzheimer's" into structured filters (phase, condition, status, keywords, etc.)
- **Spell correction** — LLM-based correction of typos and medical terms before searching
- **AI summaries** — RAG-generated summaries of search results (user query + interpretation + trials)
- **Thinking message** — Short "thinking" sentence shown while a search runs
- **Paginated results** — Load more trials with a "Show more" button
- **Trial details** — View full trial info (summary, description, eligibility, locations, etc.) in a modal

---

## Tech Stack

| Layer | Stack |
|-------|-------|
| **Backend** | Python, FastAPI, Elasticsearch, OpenAI API, RAG - Retrival Augmented Generation |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS |
| **Search** | Elasticsearch with custom mapping and intent parsing |

---

## Project Structure

```
ClinicalTrialSearch/
├── backend/                 # FastAPI + Elasticsearch + RAG
│   ├── api/                 # Routes, schemas
│   ├── rag/                 # Summaries, spell correction, thinking message
│   ├── search/              # Query parser, ES query builder
│   ├── data/                # clinical_trials.json (source data)
│   ├── app.py
│   ├── config.py
│   ├── elasticsearch_mapping.py
│   ├── ingest_json.py       # Index JSON into Elasticsearch
│   └── requirements.txt
├── frontend/                # React + Vite + Tailwind
│   ├── src/
│   │   ├── api/             # Search API client
│   │   ├── components/      # SearchInput, ResultsList, TrialCard, TrialDetailModal, etc.
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Elasticsearch 8.x** (running locally or remotely)
- **OpenAI API key** (optional; for spell correction, summaries, and thinking message)

---

## Setup

### 1. Elasticsearch

Start Elasticsearch (e.g. via Docker):

```bash
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" elasticsearch:8.11.0
```

Or use an existing Elasticsearch instance. Default URL: `http://localhost:9200`.

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Configure** `backend/.env` (create if missing):

```env
ES_HOST=http://localhost:9200
INDEX_NAME=clinical_trials
DATA_DIR=data
CLINICAL_TRIALS_JSON=clinical_trials.json

# Optional: OpenAI for spell correction, summaries, thinking message
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=          # Optional: custom base URL
OPENAI_MODEL=gpt-4o-mini  # Optional: model override
```

**Ingest data** into Elasticsearch (run once):

```bash
cd backend
python -m ingest_json
```

**Start the API:**

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

To point at a different API URL, set `VITE_API_URL` (e.g. in `frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
```

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/search/{query}` | Search trials. Optional: `?page=1&size=10` |
| GET | `/search/thinking/{query}` | LLM "thinking" message for display while search runs |
| GET | `/trial/{nct_id}` | Full trial details by NCT ID |

---

## Usage

1. Open the app and enter a natural-language query, e.g.:
   - List all the Phase 2 trials for Breast Cancer associated with BRCA1 gene
2. Results appear with an AI summary. Use **Show more** to load the next page.
3. Click **View details** on a trial to open full info (summary, description, eligibility, locations, etc.).

---