# ClearNote AI

ClearNote AI is a privacy-conscious AI application that transforms recorded conversations into searchable transcripts and structured notes containing summaries, decisions, action items, key points, and follow-up questions.

The project is being developed incrementally as a production-oriented AI engineering portfolio project.

## Current Status

The **backend MVP is now functionally complete**.

ClearNote AI currently supports:

* FastAPI backend
* Next.js frontend foundation
* Audio file upload
* Audio MIME-type and file-size validation
* Local audio file storage
* UUID-based recording identifiers
* SQLite database persistence
* SQLAlchemy async ORM
* Alembic database migrations
* Recording retrieval, listing, pagination, and deletion
* Local Whisper speech-to-text transcription
* Whisper model caching
* Transcription status tracking
* Full transcript persistence
* Timestamped transcript segments
* Transcript retrieval API
* OpenAI LLM integration
* Schema-constrained structured note generation
* Pydantic validation of LLM responses
* Generated-note persistence
* Prompt version tracking
* LLM model tracking
* Generated-note retrieval
* Duplicate generation protection
* API failure handling
* Interactive OpenAPI documentation
* Automated backend tests

The next major development phase is the frontend product experience.

---

## What ClearNote AI Does

The complete backend workflow is:

```text
Audio Recording
      ↓
Upload through FastAPI
      ↓
Validate file
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
Send transcript to OpenAI LLM
      ↓
Generate structured notes
      ↓
Validate response with Pydantic
      ↓
Persist generated notes
      ↓
Retrieve through REST APIs
```

The result is a structured representation of a recorded conversation rather than only raw transcription text.

---

## Example Output

Given a conversation such as:

```text
Vijay: The API testing is complete.
Sarah: Great. Let's deploy the new version on Friday.
Vijay: I still need to finish the database migration.
Sarah: Please complete that before deployment.
```

ClearNote AI can generate structured notes similar to:

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

The LLM is instructed to only include information supported by the transcript and to avoid inventing missing owners, dates, decisions, or facts.

---

# Architecture

```text
┌───────────────────────┐
│   Next.js Frontend    │
│      (in progress)    │
└───────────┬───────────┘
            │
            │ HTTP / JSON
            ▼
┌───────────────────────┐
│    FastAPI Backend    │
│                       │
│ Upload                │
│ Recording management  │
│ Transcription API     │
│ AI Notes API          │
└───────┬────────┬──────┘
        │        │
        │        │
        ▼        ▼
┌────────────┐  ┌─────────────────┐
│   SQLite   │  │ Local Storage   │
│            │  │                 │
│ Metadata   │  │ Audio files     │
│ Transcript │  └────────┬────────┘
│ Notes      │           │
└────────────┘           ▼
                   ┌──────────────┐
                   │   Whisper    │
                   │              │
                   │ Audio → Text │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ OpenAI LLM   │
                   │              │
                   │ Text →       │
                   │ Structured   │
                   │ Notes        │
                   └──────────────┘
```

---

# Why Whisper and an LLM Are Separate

ClearNote AI separates speech recognition from language understanding.

Whisper performs:

```text
Audio → Text
```

The OpenAI LLM performs:

```text
Transcript → Structured understanding
```

This separation makes each stage independently testable and replaceable.

For example:

```text
Audio
  ↓
Local Whisper
  ↓
Transcript
  ↓
OpenAI LLM
  ↓
Summary
Decisions
Action Items
Key Points
Follow-up Questions
```

If transcription quality is poor, the Whisper stage can be investigated independently.

If note generation is poor, the transcript remains available to evaluate the LLM stage separately.

---

# Technology Stack

## Backend

* Python 3.11
* FastAPI
* Pydantic
* Pydantic Settings
* SQLAlchemy 2
* SQLAlchemy AsyncIO
* SQLite
* aiosqlite
* Alembic
* OpenAI Whisper
* PyTorch
* OpenAI Python SDK
* Pytest
* HTTPX

## Frontend

* Next.js
* TypeScript
* Tailwind CSS

## Infrastructure / Development

* Git
* GitHub
* FFmpeg
* Docker Desktop
* SQLite CLI
* FastAPI OpenAPI documentation

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
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── generated_note.py
│   │   │   ├── recording.py
│   │   │   └── transcript.py
│   │   ├── schemas/
│   │   │   ├── generated_note.py
│   │   │   ├── recording.py
│   │   │   └── transcript.py
│   │   ├── services/
│   │   │   ├── ai_notes.py
│   │   │   ├── audio_storage.py
│   │   │   ├── generated_notes.py
│   │   │   └── transcription.py
│   │   └── main.py
│   ├── migrations/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── storage/
│   │   └── audio/
│   │       └── .gitkeep
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_notes.py
│   │   └── test_recordings.py
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
├── docs/
├── evals/
├── infrastructure/
├── .gitignore
└── README.md
```

---

# Backend Setup

From the project root:

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

Apply database migrations:

```bash
python -m alembic upgrade head
```

Start FastAPI:

```bash
python -m fastapi dev app/main.py
```

Backend URLs:

* API: `http://localhost:8000`
* API documentation: `http://localhost:8000/docs`
* Health check: `http://localhost:8000/health`

---

# Environment Configuration

Example backend configuration:

```env
DATABASE_URL=sqlite+aiosqlite:///./clearnote.db

WHISPER_MODEL_NAME=tiny
WHISPER_DEVICE=cpu

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
```

`OPENAI_API_KEY` must contain a valid OpenAI API credential in the local `.env` file.

Never commit the real API key.

Verify configuration without exposing the secret:

```bash
python -c "
from app.core.config import settings
print('API key configured:', bool(settings.openai_api_key))
print('OpenAI model:', settings.openai_model)
print('Whisper model:', settings.whisper_model_name)
"
```

---

# Database Design

The current database contains four primary application tables:

```text
recordings
transcripts
transcript_segments
generated_notes
```

The relationships are:

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

## Recordings

Stores:

* Recording ID
* Original filename
* Stored filename
* MIME type
* File size
* Processing status
* Transcription error
* Transcription start time
* Transcription completion time
* Creation timestamp

## Transcripts

Stores:

* Transcript ID
* Recording ID
* Full transcript text
* Detected language
* Whisper model name
* Audio duration
* Processing duration
* Creation timestamp

## Transcript Segments

Stores:

* Segment ID
* Transcript ID
* Segment order
* Start time
* End time
* Segment text
* Average log probability
* No-speech probability

## Generated Notes

Stores:

* Generated-note ID
* Transcript ID
* Summary
* Decisions
* Action items
* Key points
* Follow-up questions
* OpenAI model name
* Prompt version
* Creation timestamp

---

# Audio Upload

Endpoint:

```text
POST /api/recordings
```

The backend:

1. Validates the uploaded file.
2. Checks the MIME type.
3. Checks the maximum file size.
4. Generates a UUID.
5. Stores the audio locally.
6. Persists recording metadata.

Supported MIME types include:

* `audio/mpeg`
* `audio/mp4`
* `audio/x-m4a`
* `audio/wav`
* `audio/x-wav`
* `audio/webm`

Maximum upload size:

```text
25 MB
```

Uploaded audio is stored under:

```text
backend/storage/audio/
```

---

# Recording Management APIs

| Method   | Endpoint                         | Description                |
| -------- | -------------------------------- | -------------------------- |
| `POST`   | `/api/recordings`                | Upload audio               |
| `GET`    | `/api/recordings`                | List recordings            |
| `GET`    | `/api/recordings/{recording_id}` | Retrieve a recording       |
| `DELETE` | `/api/recordings/{recording_id}` | Delete recording and audio |

Pagination is supported through:

```text
?limit=20&offset=0
```

---

# Local Whisper Transcription

Endpoint:

```text
POST /api/recordings/{recording_id}/transcribe
```

Whisper is used locally as the speech-recognition engine.

The workflow is:

```text
Recording status = uploaded
        ↓
Recording status = transcribing
        ↓
Whisper processes stored audio
        ↓
Full transcript generated
        ↓
Timestamped segments generated
        ↓
Transcript persisted
        ↓
Recording status = transcribed
```

If transcription fails:

```text
status = failed
```

and an error message is stored.

## Why Local Whisper?

Running Whisper locally allows the audio-processing stage to stay on the machine running the backend.

It also cleanly separates:

```text
Speech recognition
        ↓
Language understanding
```

Whisper performs transcription, while the LLM performs summarization and structured extraction.

## Model Caching

The Whisper model is cached after its first load rather than reloaded for every transcription request.

Conceptually:

```text
First request
    ↓
Load Whisper
    ↓
Cache model
    ↓
Transcribe

Later requests
    ↓
Reuse model
```

---

# Transcript API

Retrieve an existing transcript:

```text
GET /api/recordings/{recording_id}/transcript
```

The response contains:

* Full transcript
* Language
* Whisper model
* Processing duration
* Timestamped transcript segments

---

# Structured AI Note Generation

Endpoint:

```text
POST /api/recordings/{recording_id}/generate-notes
```

The backend retrieves the persisted transcript and sends it to the configured OpenAI model.

The workflow is:

```text
Persisted transcript
        ↓
Prompt construction
        ↓
OpenAI LLM
        ↓
Schema-constrained output
        ↓
Pydantic validation
        ↓
GeneratedNote persistence
        ↓
Structured API response
```

## Structured Output Schema

The expected AI result includes:

```json
{
  "summary": "Concise summary",
  "decisions": [],
  "action_items": [],
  "key_points": [],
  "follow_up_questions": []
}
```

Action items follow a schema similar to:

```json
{
  "task": "Complete database migration",
  "owner": "Vijay",
  "due_date": null
}
```

The LLM does not directly write arbitrary JSON into the database.

Instead:

```text
OpenAI result
      ↓
GeneratedNoteContent
      ↓
Pydantic validation
      ↓
Database persistence
```

This provides a predictable API contract.

---

# Prompt Guardrails

The prompt instructs the model to:

* Use only information supported by the transcript.
* Avoid inventing names.
* Avoid inventing deadlines.
* Avoid inventing owners.
* Avoid inventing decisions.
* Return `null` when information is unknown.
* Keep summaries concise.
* Identify unresolved questions separately.

The prompt version is stored with each generated note.

Example:

```text
prompt_version = v1
```

This makes future prompt changes traceable.

---

# Generated Notes API

Generate notes:

```text
POST /api/recordings/{recording_id}/generate-notes
```

Retrieve previously generated notes:

```text
GET /api/recordings/{recording_id}/notes
```

If notes already exist, the backend returns the stored result instead of unnecessarily calling the LLM again.

This reduces:

* API cost
* Latency
* Duplicate database records
* Unnecessary model requests

---

# Error Handling

The backend handles several failure scenarios.

Examples include:

```text
Recording not found
→ 404
```

```text
Transcript not found
→ 404 / 409 depending on operation
```

```text
Generate notes before transcription
→ 409
```

```text
OpenAI generation failure
→ 502
```

```text
Database persistence failure
→ rollback
```

```text
Unsupported audio type
→ 415
```

---

# Testing Strategy

The backend uses automated tests with Pytest and HTTPX.

Tests cover areas such as:

* Health checks
* Audio upload
* File validation
* Recording persistence
* Recording retrieval
* Recording listing
* Pagination
* Recording deletion
* Audio-file cleanup
* Missing recordings
* Transcript workflow
* Generated note generation
* Generated note retrieval
* Missing transcript handling
* Duplicate generation protection
* LLM failure handling

## Mocking OpenAI

Automated tests do not make real paid OpenAI requests.

The production function:

```text
generate_note_content()
```

is replaced during tests with a deterministic mock.

Conceptually:

```text
Production
API → OpenAI → Structured result

Testing
API → Mock function → Predictable result
```

This makes tests:

* Fast
* Free
* Deterministic
* Independent of external API availability

---

# API Overview

| Method   | Endpoint                              | Purpose                  |
| -------- | ------------------------------------- | ------------------------ |
| `GET`    | `/health`                             | Health check             |
| `POST`   | `/api/recordings`                     | Upload audio             |
| `GET`    | `/api/recordings`                     | List recordings          |
| `GET`    | `/api/recordings/{id}`                | Retrieve recording       |
| `DELETE` | `/api/recordings/{id}`                | Delete recording         |
| `POST`   | `/api/recordings/{id}/transcribe`     | Run Whisper              |
| `GET`    | `/api/recordings/{id}/transcript`     | Retrieve transcript      |
| `POST`   | `/api/recordings/{id}/generate-notes` | Generate AI notes        |
| `GET`    | `/api/recordings/{id}/notes`          | Retrieve generated notes |

---

# Run Tests

From the backend directory:

```bash
source .venv/bin/activate
pytest -v
```

The goal is for all tests to run without requiring real OpenAI API requests.

---

# Backend MVP

The backend MVP now provides an end-to-end AI processing pipeline:

```text
Audio
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
OpenAI LLM
   ↓
Structured Notes
   ↓
REST API
```

This demonstrates:

* Backend API design
* Async Python
* Relational data modeling
* Database migrations
* Audio processing
* Local ML inference
* LLM integration
* Structured outputs
* Prompt engineering
* Error handling
* Model metadata tracking
* Testing and mocking
* Production-oriented separation of concerns

---

# Development Roadmap

## Completed

* Backend project foundation
* FastAPI application
* Next.js frontend foundation
* Audio upload
* File validation
* Local storage
* SQLite
* SQLAlchemy async ORM
* Alembic migrations
* Recording management
* Whisper integration
* Model caching
* Transcript persistence
* Timestamped transcript segments
* Transcription status tracking
* OpenAI API integration
* Structured LLM output
* Pydantic validation
* Prompt version tracking
* Generated-note persistence
* Generated-note retrieval
* Duplicate-generation handling
* Automated backend testing

## Next — Frontend MVP

Build:

* Audio upload interface
* Recording list
* Processing-status indicators
* Transcription trigger
* Transcript viewer
* Timestamp display
* Generate-notes action
* Structured notes viewer
* Summary display
* Decisions display
* Action-item display
* Follow-up-question display

## Later — Productionization

Potential improvements:

* Background job queue
* Redis / Celery or cloud queue
* PostgreSQL
* Amazon S3
* Authentication
* Authorization
* Docker Compose
* CI/CD
* AWS deployment
* Terraform
* Structured logging
* Observability
* Cost tracking
* LLM evaluation framework
* Human review workflow
* JSON and Markdown exports

---

# Security and Privacy

The current project is intended for development and portfolio demonstration.

Do not upload real:

* Protected health information
* Personally identifiable information
* Confidential company recordings
* Sensitive legal information
* Sensitive financial information

Use synthetic, public, or personally created test audio.

Never commit:

* OpenAI API keys
* AWS credentials
* Database passwords
* JWT signing secrets

---

# Local Files Excluded From Git

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

## License

Copyright © 2026 Vijay. All Rights Reserved.

This repository is publicly available for portfolio and demonstration
purposes only.

No permission is granted to copy, modify, distribute, sublicense,
commercialize, or create derivative works from this code without prior
written permission.

See the `LICENSE` file for details.
