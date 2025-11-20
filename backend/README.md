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

## CORS Configuration

The backend has CORS middleware configured to accept requests from allowed origins. By default, it allows:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

### Adding GitHub Pages Origin

If you're hosting the frontend on GitHub Pages, add your GitHub Pages URL to the allowed origins in `app/main.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://USERNAME.github.io",  # Add your GitHub Pages URL
],
```

Replace `USERNAME` with your actual GitHub username.

**Security Note:** For production deployments, replace `allow_origins=["*"]` with specific allowed origins to prevent unauthorized access.

## API Endpoints

- `GET /`: Root endpoint
- `GET /health`: Health check
- `POST /api/v1/generate`: Submit generation request
- `GET /api/v1/jobs/{job_id}`: Get job status
- `GET /api/v1/versions/{version_id}/audio`: Download audio file

See `/docs` for interactive API documentation.

