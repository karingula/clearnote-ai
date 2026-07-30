# ClearNote AI

ClearNote AI is a privacy-conscious AI application that transforms recorded conversations into reviewable transcripts, structured summaries, decisions, and action items.

The project is being built incrementally as a production-oriented AI engineering portfolio project.

## Current Status

The application currently supports:

* FastAPI backend
* Next.js frontend
* Frontend-to-backend connectivity
* API health check
* Audio file uploads
* Audio type and size validation
* Local audio file storage
* Unique recording IDs
* SQLite database persistence
* SQLAlchemy async ORM
* Recording metadata retrieval by ID
* Automated backend tests
* Interactive OpenAPI documentation

## Current Workflow

```text
Upload audio
    ↓
Validate file type and size
    ↓
Generate a unique recording ID
    ↓
Store the audio file locally
    ↓
Save recording metadata in SQLite
    ↓
Return the persisted recording
    ↓
Retrieve the recording later by ID
```

Transcription and AI-generated structured notes will be added in later phases.

## Technology Stack

### Backend

* Python 3.11
* FastAPI
* Pydantic
* Pydantic Settings
* SQLAlchemy 2
* SQLAlchemy AsyncIO
* SQLite
* aiosqlite
* Pytest
* HTTPX

### Frontend

* Next.js
* TypeScript
* Tailwind CSS

### Development Tools

* Git and GitHub
* FFmpeg
* Docker Desktop
* FastAPI interactive documentation

## Project Structure

```text
clearnote-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── recordings.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   └── recording.py
│   │   ├── schemas/
│   │   │   └── recording.py
│   │   ├── services/
│   │   │   └── audio_storage.py
│   │   └── main.py
│   ├── storage/
│   │   └── audio/
│   │       └── .gitkeep
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
├── docs/
├── evals/
├── infrastructure/
├── .gitignore
└── README.md
```

## Prerequisites

Install the following tools:

* Python 3.11
* Node.js 20.9 or newer
* npm
* FFmpeg
* Docker Desktop
* Git

## Backend Setup

From the project root:

```bash
cd backend

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create the local backend environment file:

```bash
cp .env.example .env
```

The default local configuration is:

```env
DATABASE_URL=sqlite+aiosqlite:///./clearnote.db
```

Start the backend:

```bash
python -m fastapi dev app/main.py
```

Backend URLs:

* API: `http://localhost:8000`
* API documentation: `http://localhost:8000/docs`
* Health check: `http://localhost:8000/health`

## Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

## Database

ClearNote AI currently uses SQLite for local development.

The database file is created at:

```text
backend/clearnote.db
```

The file is excluded from Git.

The backend uses:

* `create_async_engine`
* `AsyncSession`
* `async_sessionmaker`
* `aiosqlite`
* SQLAlchemy declarative models

### Recording Table

Each uploaded recording persists the following metadata:

* Recording ID
* Original filename
* Stored filename
* Content type
* File size
* Processing status
* Creation timestamp

Recording IDs use SQLAlchemy's database-agnostic UUID type. SQLite stores the UUID as a character value while the Python application works with `UUID` objects.

### Inspect the Local Database

From the backend directory:

```bash
sqlite3 clearnote.db
```

List tables:

```sql
.tables
```

Inspect the recordings schema:

```sql
.schema recordings
```

View stored recordings:

```sql
SELECT
    id,
    original_filename,
    content_type,
    size_bytes,
    status,
    created_at
FROM recordings;
```

Exit SQLite:

```sql
.quit
```

## Audio Upload

The upload endpoint is:

```text
POST /api/recordings
```

The request must use `multipart/form-data` with a field named:

```text
file
```

Supported MIME types:

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

Uploaded files are stored locally in:

```text
backend/storage/audio/
```

Uploaded media files are excluded from Git.

### Test Through FastAPI Docs

1. Open `http://localhost:8000/docs`.
2. Expand `POST /api/recordings`.
3. Click **Try it out**.
4. Select an audio file.
5. Click **Execute**.

A successful upload returns HTTP `201`.

### Test With curl

```bash
curl -X POST \
  "http://localhost:8000/api/recordings" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/sample.m4a;type=audio/mp4"
```

Example response:

```json
{
  "id": "4202365a-f1f6-4729-a318-82191ee5c1cb",
  "original_filename": "sample.m4a",
  "stored_filename": "4202365a-f1f6-4729-a318-82191ee5c1cb.m4a",
  "content_type": "audio/mp4",
  "size_bytes": 74993,
  "status": "uploaded",
  "created_at": "2026-07-30T12:21:34.819959Z"
}
```

## Retrieve a Recording

The retrieval endpoint is:

```text
GET /api/recordings/{recording_id}
```

Example:

```bash
curl \
  "http://localhost:8000/api/recordings/4202365a-f1f6-4729-a318-82191ee5c1cb"
```

A successful request returns HTTP `200` with the persisted recording metadata.

An unknown recording ID returns HTTP `404`.

## API Endpoints

| Method | Endpoint                         | Description                                       |
| ------ | -------------------------------- | ------------------------------------------------- |
| GET    | `/health`                        | Returns API health information                    |
| POST   | `/api/recordings`                | Validates, stores and persists an audio recording |
| GET    | `/api/recordings/{recording_id}` | Retrieves recording metadata by ID                |

## Run Tests

From the backend directory:

```bash
source .venv/bin/activate
pytest -v
```

Current tests cover:

* Health-check response
* Successful audio upload
* Unsupported file rejection
* Empty audio-file rejection

Database integration tests will be expanded in the next phase.

## Development Roadmap

### Completed

* Project foundation
* FastAPI backend setup
* Next.js frontend setup
* Frontend-to-backend connection
* Health-check endpoint
* Audio upload API
* File type validation
* File size validation
* Local audio storage
* SQLite database setup
* SQLAlchemy async integration
* Recording database model
* Recording persistence
* Recording retrieval by ID

### Next

* Database integration tests
* Alembic migrations
* Recording list endpoint
* Recording deletion and cleanup
* Local Whisper transcription
* Timestamped transcript segments
* Recording processing status updates
* Structured AI note generation
* Human review and editing
* JSON and Markdown export
* Docker Compose
* PostgreSQL
* Background job processing
* AWS deployment
* Terraform infrastructure

## Security and Privacy

This project is currently intended for development and portfolio demonstration.

Do not upload:

* Protected health information
* Personally identifiable information
* Confidential company recordings
* Sensitive legal or financial conversations

Use synthetic, public, or personally created test audio only.

Frontend environment variables prefixed with `NEXT_PUBLIC_` are visible to browser users and must never contain secrets.

API keys, database credentials, AWS credentials, and signing secrets must only be stored in backend environment variables.

## Local Files Excluded From Git

The following local files should not be committed:

```text
backend/.env
backend/clearnote.db
backend/.venv/
backend/storage/audio/*
frontend/.env.local
frontend/node_modules/
frontend/.next/
```

The storage placeholder remains tracked:

```text
backend/storage/audio/.gitkeep
```

## License

A license has not yet been selected.
