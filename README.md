# ClearNote AI

ClearNote AI is a privacy-conscious AI application that transforms recorded conversations into reviewable transcripts, structured summaries, decisions, and action items.

## Current Status

The project currently supports:

* FastAPI backend
* Next.js frontend
* Frontend-to-backend connectivity
* API health check
* Audio file uploads
* Audio file type validation
* Maximum upload size enforcement
* Local audio storage
* Unique recording IDs
* Automated backend tests
* Interactive API documentation

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
Return recording metadata
```

Transcription and AI-generated notes will be added in later phases.

## Technology Stack

### Backend

* Python 3.11
* FastAPI
* Pydantic
* Pytest
* HTTPX

### Frontend

* Next.js
* TypeScript
* Tailwind CSS

### Development Tools

* Git and GitHub
* FFmpeg
* Docker
* FastAPI interactive documentation

## Project Structure

```text
clearnote-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── storage/
│   │   └── audio/
│   ├── tests/
│   └── requirements.txt
├── frontend/
├── docs/
├── evals/
├── infrastructure/
├── .gitignore
└── README.md
```

## Local Development

### Prerequisites

Install:

* Python 3.11
* Node.js 20.9 or newer
* npm
* FFmpeg
* Docker Desktop

## Backend Setup

From the project root:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
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
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Upload an Audio Recording

The upload endpoint is:

```text
POST /api/recordings
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
  "id": "94e0e04f-f484-42ad-8821-63bc35741fd7",
  "original_filename": "sample.m4a",
  "stored_filename": "94e0e04f-f484-42ad-8821-63bc35741fd7.m4a",
  "content_type": "audio/mp4",
  "size_bytes": 582013,
  "status": "uploaded",
  "created_at": "2026-07-29T13:00:00Z"
}
```

Uploaded audio files are stored locally in:

```text
backend/storage/audio/
```

Uploaded media files are excluded from Git.

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

## API Endpoints

| Method | Endpoint          | Description                             |
| ------ | ----------------- | --------------------------------------- |
| GET    | `/health`         | Returns API health information          |
| POST   | `/api/recordings` | Validates and stores an audio recording |

## Development Roadmap

### Completed

* Project foundation
* Backend and frontend setup
* Health-check endpoint
* Frontend-to-backend connection
* Audio upload API
* File validation
* Local audio storage
* Automated upload tests

### Next

* SQLite and SQLAlchemy persistence
* Recording retrieval endpoints
* Recording status tracking
* Local Whisper transcription
* Timestamped transcript segments
* Structured AI note generation
* Human review and editing
* Export to JSON and Markdown
* Docker Compose
* PostgreSQL
* Background processing
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

## License

A license has not yet been selected.
