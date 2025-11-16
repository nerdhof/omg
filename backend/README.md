# Backend API

FastAPI backend service that orchestrates music generation requests.

## Setup

1. Install dependencies using uv:
```bash
# Install uv if not already installed: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

This will create a virtual environment (`.venv`) and install all dependencies from `pyproject.toml`.

## Running

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker build -t backend .
docker run -p 8000:8000 backend
```

## Environment Variables

- `BACKEND_PORT`: Port to run on (default: 8000)
- `MODEL_SERVICE_URL`: URL of the model service (default: http://localhost:8001)

## API Endpoints

- `GET /`: Root endpoint
- `GET /health`: Health check
- `POST /api/v1/generate`: Submit generation request
- `GET /api/v1/jobs/{job_id}`: Get job status
- `GET /api/v1/versions/{version_id}/audio`: Download audio file

See `/docs` for interactive API documentation.

