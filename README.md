# Music Generation Web Application

A web application for generating music using AI models (starting with ACE-Step) with a microservices architecture.

## Architecture

- **Frontend**: Vue.js application for user interface
- **Backend API**: FastAPI service that orchestrates requests
- **Model Service**: FastAPI microservice running ACE-Step model locally

## Project Structure

```
omg/
├── frontend/          # Vue.js application
├── backend/           # Main FastAPI application
├── model-service/     # ACE-Step microservice
└── docker-compose.yml # Service orchestration
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- uv (Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker and Docker Compose (optional)

### Development Setup

1. **Model Service**:
   ```bash
   cd model-service
   # Install uv if not already installed: curl -LsSf https://astral.sh/uv/install.sh | sh
   uv sync
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Backend**:
   ```bash
   cd backend
   # Install uv if not already installed: curl -LsSf https://astral.sh/uv/install.sh | sh
   uv sync
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Frontend**:
   ```bash
   cd frontend
   npm install
   ```

### Running Services

1. Start model service:
   ```bash
   cd model-service
   uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

2. Start backend API:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. Start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

### Docker Compose

```bash
docker-compose up
```

## API Documentation

- Backend API: http://localhost:8000/docs
- Model Service: http://localhost:8001/docs

## Environment Variables

### Model Service
- `MODEL_SERVICE_PORT`: Port to run on (default: 8001)
- `ACE_STEP_MODEL_PATH`: Path to ACE-Step model checkpoint (optional)
- `DEVICE`: Device to use ('cpu' or 'cuda', default: 'cpu')

### Backend
- `BACKEND_PORT`: Port to run on (default: 8000)
- `MODEL_SERVICE_URL`: URL of the model service (default: http://localhost:8001)

### Frontend
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## ACE-Step Model Setup

**Important**: The ACE-Step model implementation is currently a placeholder. To use the actual model:

1. Install ACE-Step according to its official documentation
2. Update `model-service/app/models/ace_step.py` with the actual model loading and generation code
3. Add required dependencies to `model-service/requirements.txt`
4. Configure model path via `ACE_STEP_MODEL_PATH` environment variable

The current implementation provides the complete infrastructure - you just need to integrate the actual ACE-Step model API.

## Features

- **Music Generation**: Generate music based on style, topic, refrain, or complete text
- **Multiple Versions**: Generate 1-5 versions per request
- **Real-time Status**: Poll job status and track generation progress
- **Audio Playback**: Play generated versions directly in the browser
- **Download**: Download generated audio files

## Development Notes

- Job management is currently in-memory (jobs are lost on restart)
- Audio files are stored locally in temporary directories
- For production, consider:
  - Database for job persistence (Redis, PostgreSQL)
  - Cloud storage for audio files (S3, Azure Blob)
  - Authentication and authorization
  - Rate limiting
  - Better error handling and retry logic

## Troubleshooting

- **Model service not responding**: Check that the model service is running on port 8001
- **CORS errors**: Ensure backend CORS settings include your frontend URL
- **Audio files not found**: Verify that the model service is generating files correctly

