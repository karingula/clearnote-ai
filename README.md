# ClearNote AI

ClearNote AI transforms recorded conversations into reviewable transcripts,
structured summaries, decisions and action items.

## Current status

The project currently contains:

- A FastAPI backend
- A Next.js frontend
- A backend health endpoint
- Frontend-to-backend connectivity
- An automated backend test

## Local development

### Backend

```bash
cd backend
source .venv/bin/activate
fastapi dev app/main.py
