# Clinical Trial Search — Presentation Outline

Copy each slide into PowerPoint. Keep slides short with bullet points.

---

## Slide 1: Title

**Clinical Trial Search**  
*Discover clinical trials that match—not the other way around.*

---

## Slide 2: Problem & Solution

**Problem & Solution**

- Finding relevant clinical trials is hard (keywords, filters, jargon)
- Users think in natural language, not structured filters
- Solution: Natural-language search with AI-powered summaries

---

## Slide 3: Key Features

**Key Features**

- Natural language search (e.g. "Phase 2 breast cancer trials")
- Spell correction for typos and medical terms
- AI summaries of results (RAG)
- Thinking message while search runs
- Show more pagination
- Full trial details modal

---

## Slide 4: Tech Stack

**Tech Stack**

| Backend | Frontend |
|---------|----------|
| Python, FastAPI | React 19, TypeScript |
| Elasticsearch | Vite |
| OpenAI (optional) | Tailwind CSS |
| RAG for summaries | |

---

## Slide 5: Architecture

**Architecture**

- User query → Spell correction (LLM) → Query parser → Elasticsearch
- ES results → Summary generation (RAG) → Response
- Trial details: GET /trial/{nct_id} on demand
- Minimal list payload; full details fetched only when "View details" is clicked

---

## Slide 6: API Endpoints

**API Endpoints**

- GET /search/{query} — Search trials (?page, ?size)
- GET /search/thinking/{query} — LLM "thinking" message
- GET /trial/{nct_id} — Full trial details by NCT ID

---

## Slide 7: UX Highlights

**UX Highlights**

- Chat-like interface: user query + assistant summary + results
- Clear progress: "Thinking…" while search runs
- Load more with skeleton loading
- Modal for trial details (gray overlay, response-style background)

---

## Slide 8: Setup & Run

**Setup & Run**

- Elasticsearch 8.x (Docker or local)
- Backend: Python venv, pip install, ingest data, uvicorn
- Frontend: npm install, npm run dev
- Optional: OPENAI_API_KEY for AI features

---

## Slide 9: Thank You

**Thank You**  
*Questions?*
