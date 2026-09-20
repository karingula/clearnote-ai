# ClearNote AI

**Privacy-Conscious Conversation Intelligence**

ClearNote AI is an AI-powered application that transforms recorded conversations into searchable transcripts and structured notes containing summaries, decisions, action items, key points, and follow-up questions.

The project is being developed incrementally as a production-oriented AI engineering portfolio project.

---

## Current Status

The **backend MVP is complete** and the **frontend MVP is functional and persistent across browser refreshes**.

ClearNote AI currently supports:

- Audio file upload
- Audio MIME-type and file-size validation
- Local audio file storage
- UUID-based recording identifiers
- SQLite database persistence
- SQLAlchemy async ORM
- Alembic database migrations
- Recording retrieval, listing, pagination, and deletion
- Local Whisper speech-to-text transcription
- Whisper model caching
- Transcription status tracking
- Full transcript persistence
- Timestamped transcript segments
- Transcript retrieval API
- OpenAI LLM integration
- Schema-constrained structured note generation
- Pydantic validation of LLM responses
- Generated-note persistence
- Prompt version tracking
- LLM model tracking
- Duplicate generation protection
- Development mock-AI mode
- FastAPI error handling
- Automated backend tests
- Next.js frontend
- Recording history workspace
- Historical recording reopening
- Persisted recording selection through the URL
- Automatic transcript and note restoration after refresh
- Loading and error states
- Indigo + slate visual theme
- Interactive FastAPI OpenAPI documentation

The next development phase focuses on improving the user experience, component structure, human review/editing, and export capabilities.

---

# What ClearNote AI Does

The complete application workflow is:

```text
Audio Recording
      ↓
Next.js Frontend
      ↓
Upload through FastAPI
      ↓
Validate audio
      ↓
Store audio locally
      ↓
Persist recording metadata
      ↓
Run local Whisper
      ↓
Generate transcript
      ↓
Persist full transcript
      ↓
Persist timestamped segments
      ↓
Generate structured AI notes
      ↓
Validate structured output
      ↓
Persist generated notes
      ↓
Display transcript + notes
      ↓
Reopen them later without reprocessing
```

The goal is not simply to transcribe audio.

ClearNote AI turns an unstructured conversation into structured, reviewable information.

---

# Example

Given a conversation such as:

```text
Vijay: The API testing is complete.
Sarah: Great. Let's deploy the new version on Friday.
Vijay: I still need to finish the database migration.
Sarah: Please complete that before deployment.
```

ClearNote AI can generate structured output such as:

```json
{
  "summary": "The team discussed deployment readiness and the remaining database migration.",
  "decisions": [
    "Deploy the new version on Friday."
  ],
  "action_items": [
    {
      "task": "Complete the database migration before deployment.",
      "owner": "Vijay",
      "due_date": null
    }
  ],
  "key_points": [
    "API testing is complete.",
    "The database migration remains outstanding."
  ],
  "follow_up_questions": []
}
```

The LLM is instructed to use only information supported by the transcript and avoid inventing owners, dates, decisions, deadlines, or facts.

---

# Architecture

```text
┌───────────────────────────────┐
│        Next.js Frontend       │
│                               │
│ Upload                        │
│ Recording workspace           │
│ Recording history             │
│ Transcript viewer             │
│ AI notes viewer               │
│ URL-persisted selection       │
└──────────────┬────────────────┘
               │
               │ HTTP / JSON
               ▼
┌───────────────────────────────┐
│        FastAPI Backend        │
│                               │
│ Recording API                 │
│ Transcription API             │
│ AI Notes API                  │
└───────┬───────────────┬───────┘
        │               │
        ▼               ▼
┌───────────────┐  ┌──────────────────┐
│    SQLite     │  │  Local Storage   │
│               │  │                  │
│ Recordings    │  │  Audio files     │
│ Transcripts   │  └─────────┬────────┘
│ Segments      │            │
│ AI Notes      │            ▼
└───────────────┘      ┌──────────────┐
                       │   Whisper    │
                       │              │
                       │ Audio → Text │
                       └──────┬───────┘
                              │
                              ▼
                       ┌──────────────┐
                       │ AI Notes     │
                       │              │
                       │ OpenAI API   │
                       │     or       │
                       │ Mock Mode    │
                       └──────────────┘
```

---

# AI Pipeline

ClearNote AI intentionally separates **speech recognition** from **language understanding**.

## Stage 1 — Speech Recognition

Whisper performs:

```text
Audio → Transcript
```

Whisper runs locally on the backend machine.

It produces:

- Full transcript text
- Detected language
- Timestamped segments
- Segment-level confidence metadata
- Audio duration information

## Stage 2 — Language Understanding

The LLM performs:

```text
Transcript → Structured Notes
```

The AI extracts:

- Summary
- Decisions
- Action items
- Key points
- Follow-up questions

This separation allows each AI stage to be tested, debugged, improved, and eventually replaced independently.

---

# Why Local Whisper?

ClearNote AI currently uses **OpenAI Whisper locally** for speech-to-text.

The audio is not sent to an external transcription API.

Conceptually:

```text
Uploaded Audio
      ↓
Local File
      ↓
Whisper Model
      ↓
Transcript
```

Whisper is currently configured with a small model suitable for development:

```env
WHISPER_MODEL_NAME=tiny
WHISPER_DEVICE=cpu
```

Larger Whisper models can be used later for improved transcription accuracy.

---

# Whisper Model Caching

Loading a machine-learning model for every request would be inefficient.

The Whisper model is therefore cached after its first load.

```text
First transcription
      ↓
Load Whisper
      ↓
Cache model
      ↓
Transcribe

Future transcription
      ↓
Reuse cached model
```

This avoids repeatedly loading the same model into memory.

---

# Technology Stack

## Backend

- Python 3.11
- FastAPI
- Pydantic
- Pydantic Settings
- SQLAlchemy 2
- SQLAlchemy AsyncIO
- SQLite
- aiosqlite
- Alembic
- OpenAI Whisper
- PyTorch
- OpenAI Python SDK
- Pytest
- HTTPX

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Development

- Git
- GitHub
- FFmpeg
- Docker Desktop
- SQLite CLI
- FastAPI OpenAPI documentation

---

# Project Structure

```text
clearnote-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── notes.py
│   │   │       ├── recordings.py
│   │   │       └── transcriptions.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── generated_note.py
│   │   │   ├── recording.py
│   │   │   └── transcript.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── generated_note.py
│   │   │   ├── recording.py
│   │   │   └── transcript.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_notes.py
│   │   │   ├── audio_storage.py
│   │   │   ├── generated_notes.py
│   │   │   └── transcription.py
│   │   │
│   │   └── main.py
│   │
│   ├── migrations/
│   │   └── versions/
│   │
│   ├── storage/
│   │   └── audio/
│   │       └── .gitkeep
│   │
│   ├── tests/
│   │
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx
│   │   │
│   │   ├── lib/
│   │   │   └── api.ts
│   │   │
│   │   └── types/
│   │       └── api.ts
│   │
│   └── .env.local
│
├── docs/
├── evals/
├── infrastructure/
├── LICENSE
├── .gitignore
└── README.md
```

---

# Database Design

The current application uses four primary database tables:

```text
recordings
transcripts
transcript_segments
generated_notes
```

Relationships:

```text
Recording
    │
    └── Transcript
            │
            ├── Transcript Segment
            ├── Transcript Segment
            ├── Transcript Segment
            │
            └── Generated Note
```

---

## Recordings

Stores information about uploaded audio:

- Recording ID
- Original filename
- Stored filename
- MIME type
- File size
- Processing status
- Transcription error
- Transcription start time
- Transcription completion time
- Creation timestamp

---

## Transcripts

Stores transcription results:

- Transcript ID
- Recording ID
- Full transcript text
- Detected language
- Whisper model name
- Audio duration
- Processing duration
- Creation timestamp

---

## Transcript Segments

Stores timestamped sections of the transcript:

- Segment ID
- Transcript ID
- Segment index
- Start time
- End time
- Segment text
- Average log probability
- No-speech probability

---

## Generated Notes

Stores structured AI results:

- Generated-note ID
- Transcript ID
- Summary
- Decisions
- Action items
- Key points
- Follow-up questions
- AI model name
- Prompt version
- Creation timestamp

---

# Audio Upload

Endpoint:

```text
POST /api/recordings
```

The backend:

1. Receives the uploaded audio.
2. Validates the MIME type.
3. Validates the file size.
4. Generates a UUID.
5. Stores the audio locally.
6. Persists metadata in the database.

Supported MIME types include:

```text
audio/mpeg
audio/mp4
audio/x-m4a
audio/wav
audio/x-wav
audio/webm
```

Maximum upload size:

```text
25 MB
```

Uploaded audio is stored under:

```text
backend/storage/audio/
```

---

# Recording Management

Current recording endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/recordings` | Upload audio |
| `GET` | `/api/recordings` | List recordings |
| `GET` | `/api/recordings/{id}` | Retrieve recording |
| `DELETE` | `/api/recordings/{id}` | Delete recording |

Pagination is supported:

```text
/api/recordings?limit=20&offset=0
```

The list response currently uses:

```json
{
  "items": []
}
```

The frontend API layer extracts the `items` collection before storing it in application state.

---

# Transcription

Start transcription:

```text
POST /api/recordings/{recording_id}/transcribe
```

Retrieve transcript:

```text
GET /api/recordings/{recording_id}/transcript
```

Workflow:

```text
uploaded
   ↓
transcribing
   ↓
Whisper
   ↓
transcript + segments
   ↓
transcribed
```

If transcription fails:

```text
failed
```

and the backend stores the transcription error.

---

# Structured AI Notes

Generate notes:

```text
POST /api/recordings/{recording_id}/generate-notes
```

Retrieve notes:

```text
GET /api/recordings/{recording_id}/notes
```

The generation workflow is:

```text
Persisted Transcript
        ↓
Prompt
        ↓
LLM
        ↓
Structured Response
        ↓
Pydantic Validation
        ↓
GeneratedNote
        ↓
Database
```

The expected structure is:

```json
{
  "summary": "Concise summary",
  "decisions": [],
  "action_items": [],
  "key_points": [],
  "follow_up_questions": []
}
```

Action items use a structured schema:

```json
{
  "task": "Complete database migration",
  "owner": "Vijay",
  "due_date": null
}
```

---

# Prompt Guardrails

The generation prompt instructs the model to:

- Use only information supported by the transcript
- Avoid inventing names
- Avoid inventing owners
- Avoid inventing deadlines
- Avoid inventing decisions
- Return `null` when information is unknown
- Keep summaries concise
- Keep key points factual
- Identify unresolved items as follow-up questions

---

# Prompt Version Tracking

Prompts are treated as part of application behavior.

Every generated note stores:

```text
model_name
prompt_version
created_at
```

Example:

```text
model_name = gpt-5-mini
prompt_version = v1
```

If the prompt later changes:

```text
Prompt v1
   ↓
Note A
Note B

Prompt improved

Prompt v2
   ↓
Note C
Note D
```

Existing notes still retain the version that created them.

This provides traceability for:

- Debugging
- Prompt evaluation
- Regression analysis
- Hallucination analysis
- Model comparison
- Reproducibility

---

# Duplicate Generation Protection

If generated notes already exist for a transcript, ClearNote AI returns the persisted result instead of unnecessarily calling the LLM again.

This avoids:

- Duplicate records
- Additional API cost
- Increased latency
- Unnecessary model calls

---

# Mock AI Development Mode

ClearNote AI supports an optional **mock AI mode** so the complete application can be developed and demonstrated without requiring paid API usage.

Backend configuration:

```env
MOCK_AI=true
```

When mock mode is enabled:

```text
Generate Notes
      ↓
FastAPI
      ↓
Mock note generator
      ↓
Structured GeneratedNoteContent
      ↓
Database
      ↓
Frontend
```

No OpenAI API request is made.

This allows development of:

- Frontend workflows
- Database persistence
- API behavior
- Loading states
- Error handling
- Historical recording restoration

without spending API credits.

To use the real OpenAI integration:

```env
MOCK_AI=false
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5-mini
```

The application architecture remains the same regardless of which mode is used.

---

# Frontend Workspace

The frontend now provides a persistent recording workspace.

When ClearNote AI opens:

```text
Load application
      ↓
GET recent recordings
      ↓
Display recording workspace
```

Each recording card shows:

- Filename
- Creation time
- Processing status
- Suggested next action

Example:

```text
🎙️ team-meeting.m4a

Sep 20, 2026, 10:15 AM

[Transcribed]  Open transcript and notes
```

Status badges currently include:

```text
Uploaded       → Slate
Transcribing   → Indigo
Transcribed    → Green
Failed         → Red
```

---

# Reopening Historical Recordings

Historical recordings are clickable.

When a recording is selected:

```text
Click recording
      ↓
Set active recording
      ↓
Load persisted transcript
      ↓
Load persisted notes
      ↓
Restore workspace
```

The application does **not** rerun Whisper or regenerate AI notes simply because a historical recording is reopened.

Existing persisted results are reused.

If the recording has not been transcribed yet:

```text
Open recording
      ↓
No transcript
      ↓
Show Transcribe
```

If a transcript exists but notes do not:

```text
Open recording
      ↓
Restore transcript
      ↓
Show Generate Notes
```

If both exist:

```text
Open recording
      ↓
Restore transcript
      ↓
Restore AI notes
```

---

# URL-Persisted Recording Selection

The currently selected recording is stored in the browser URL.

Example:

```text
http://localhost:3000/?recording=<recording-uuid>
```

This gives the frontend a persistent source of truth for which recording is currently selected.

Flow:

```text
User clicks recording
      ↓
URL receives recording UUID
      ↓
Recording becomes highlighted
      ↓
User refreshes page
      ↓
UUID remains in URL
      ↓
Frontend reloads recording history
      ↓
Matching recording is found
      ↓
Selection is restored
      ↓
Transcript and notes are restored
```

This means a browser refresh no longer destroys the user's active workspace.

---

# Frontend State

The frontend currently manages:

- Selected audio file
- Current recording
- Recording history
- Transcript
- Generated notes
- Processing step
- Loading states
- API errors
- Recording restoration

The URL stores the selected recording ID, while persisted application data remains in the backend database.

---

# Frontend Theme

ClearNote AI uses a minimal **indigo + slate** design system.

```text
Indigo 600   Primary brand and actions
Indigo 50    Soft accent backgrounds
Slate 950    Main headings
Slate 700    Body text
Slate 500    Secondary metadata
Slate 50     Secondary panels
White        Main cards
```

The goal is a clean, modern, professional AI-product interface without unnecessary visual complexity.

---

# Backend Setup

From the repository root:

```bash
cd backend

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create local environment configuration:

```bash
cp .env.example .env
```

Apply migrations:

```bash
python -m alembic upgrade head
```

Start FastAPI:

```bash
python -m fastapi dev app/main.py
```

Backend:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

# Backend Environment Configuration

Example `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./clearnote.db

WHISPER_MODEL_NAME=tiny
WHISPER_DEVICE=cpu

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini

MOCK_AI=true
```

For free local development:

```env
MOCK_AI=true
```

For real LLM generation:

```env
MOCK_AI=false
OPENAI_API_KEY=your_api_key
```

Never commit the actual `.env` file.

---

# Frontend Setup

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

Frontend environment:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

# Running ClearNote AI Locally

Use two terminal windows.

## Terminal 1 — Backend

```bash
cd ~/Documents/Projects/clearnote-ai/backend

source .venv/bin/activate

python -m alembic upgrade head

python -m fastapi dev app/main.py
```

## Terminal 2 — Frontend

```bash
cd ~/Documents/Projects/clearnote-ai/frontend

npm run dev
```

Then open:

```text
http://localhost:3000
```

---

# API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/recordings` | Upload audio |
| `GET` | `/api/recordings` | List recordings |
| `GET` | `/api/recordings/{id}` | Retrieve recording |
| `DELETE` | `/api/recordings/{id}` | Delete recording |
| `POST` | `/api/recordings/{id}/transcribe` | Run Whisper |
| `GET` | `/api/recordings/{id}/transcript` | Retrieve transcript |
| `POST` | `/api/recordings/{id}/generate-notes` | Generate AI notes |
| `GET` | `/api/recordings/{id}/notes` | Retrieve generated notes |

---

# Error Handling

ClearNote AI handles common backend failures explicitly.

Examples:

```text
Recording not found
→ 404
```

```text
Generate notes before transcription
→ 409
```

```text
LLM generation failure
→ 502
```

```text
Unsupported audio type
→ 415
```

```text
Database persistence failure
→ rollback
```

The frontend surfaces API errors to the user rather than silently failing.

---

# Testing

The backend uses:

- Pytest
- HTTPX
- Async test clients
- Dependency overrides
- Mocked external AI calls

Tests cover functionality such as:

- Health endpoint
- Audio upload
- File validation
- Recording persistence
- Recording retrieval
- Recording listing
- Pagination
- Recording deletion
- Audio cleanup
- Missing recordings
- Transcription workflow
- Generated-note generation
- Generated-note retrieval
- Missing transcript handling
- Duplicate generation protection
- LLM failure handling

---

# Why Mock External AI Calls in Tests?

Automated tests should not depend on:

- Internet connectivity
- Paid API usage
- External API uptime
- Rate limits
- Non-deterministic model responses

Therefore:

```text
Production
API → OpenAI → Structured result

Tests
API → Mock function → Deterministic result
```

This keeps tests:

- Fast
- Free
- Repeatable
- Deterministic

---

# Frontend Quality Checks

Run:

```bash
cd frontend

npm run lint
npm run build
```

The production build validates:

- TypeScript
- React behavior
- Next.js production compatibility
- Static/prerender requirements

---

# Security and Privacy

The current project is intended for development and portfolio demonstration.

Do not upload real:

- Protected health information
- Personally identifiable information
- Confidential company recordings
- Sensitive legal information
- Sensitive financial information

Use synthetic, public, or personally created test audio.

Never commit:

- OpenAI API keys
- AWS credentials
- Database passwords
- JWT signing secrets
- `.env` files

---

# Files Excluded From Git

Do not commit:

```text
backend/.env
backend/clearnote.db
backend/.venv/
backend/storage/audio/*
frontend/.env.local
frontend/node_modules/
frontend/.next/
```

The storage placeholder may remain tracked:

```text
backend/storage/audio/.gitkeep
```

---

# Current MVP

ClearNote AI currently provides the following end-to-end flow:

```text
Audio
   ↓
Upload
   ↓
FastAPI
   ↓
Local Storage
   ↓
SQLite
   ↓
Whisper
   ↓
Transcript
   ↓
Structured AI Notes
   ↓
Persistence
   ↓
Next.js Workspace
   ↓
Historical Reopening
   ↓
Refresh Restoration
```

The project currently demonstrates:

- Backend API design
- Async Python
- Relational data modeling
- Database migrations
- File validation
- Audio processing
- Local ML inference
- LLM integration
- Structured LLM output
- Prompt engineering
- Prompt version tracking
- External-service abstraction
- Mock AI development mode
- Error handling
- Testing and mocking
- React state management
- TypeScript API contracts
- Frontend/backend integration
- Persistent application state
- URL-driven UI state
- Production frontend build validation
- AI-product UI design

---

# Development Roadmap

## Completed — Backend

- FastAPI foundation
- Audio upload
- File validation
- Local audio storage
- UUID recording IDs
- SQLite persistence
- SQLAlchemy async ORM
- Alembic migrations
- Recording listing
- Recording retrieval
- Pagination
- Recording deletion
- Whisper integration
- Whisper model caching
- Transcription status tracking
- Transcript persistence
- Timestamped transcript segments
- Transcript retrieval
- OpenAI integration
- Structured AI output
- Pydantic validation
- Prompt guardrails
- Prompt version tracking
- Model metadata tracking
- Generated-note persistence
- Generated-note retrieval
- Duplicate-generation protection
- Mock AI mode
- Automated backend testing

## Completed — Frontend

- Next.js application
- TypeScript API models
- Backend API client
- Audio file picker
- Audio upload
- Recording metadata
- Transcription action
- Transcript viewer
- Timestamped segments
- AI note generation
- Structured notes viewer
- Loading states
- Error states
- Recording history workspace
- Improved recording cards
- Recording status badges
- Historical recording reopening
- Persisted transcript restoration
- Persisted AI note restoration
- URL-based recording selection
- Selected-recording highlighting
- Selection restoration after refresh
- Indigo + slate visual design
- Production lint/build validation

## Next

- Automatically scroll to the active recording details
- Break large frontend page into reusable components
- Improve processing indicators
- Human review/editing workflow
- Save reviewed notes
- Distinguish AI-generated notes from human-edited notes
- Markdown export
- JSON export
- Improve accessibility
- Add frontend tests

## Later — Productionization

- Background transcription jobs
- Job queue
- PostgreSQL
- Amazon S3
- Authentication
- Authorization
- Retry handling
- Structured logging
- Observability
- Docker Compose
- CI/CD
- Cloud deployment
- Terraform
- LLM evaluation framework
- Cost tracking
- Human review audit trail

---

# Future AI Engineering Improvements

Potential future AI-focused work includes:

```text
Prompt versions
      ↓
Evaluation dataset
      ↓
Run prompt/model experiments
      ↓
Measure:
  - decision accuracy
  - action-item extraction
  - hallucination rate
  - missing information
      ↓
Promote better prompt/model
```

This would evolve ClearNote AI from basic prompt engineering toward a measurable LLM evaluation and deployment workflow.

---

# License

Copyright © 2026 Vijay. All Rights Reserved.

This repository is publicly available for portfolio and demonstration purposes only.

No permission is granted to copy, reproduce, modify, distribute, sublicense, publish, sell, commercially use, or create derivative works from this software without prior written permission from the copyright holder.

See the `LICENSE` file for full terms.