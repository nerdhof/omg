# Quick Start Guide

Get the music generation web app up and running in minutes.

## Prerequisites

- **Python**: 
  - Backend: 3.13+
  - Model Service: 3.11 only (>=3.11,<3.12)
- Node.js 18 or higher
- npm or yarn
- uv (Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Step-by-Step Setup

### 1. Set Up Model Service

```bash
cd model-service
# Install uv if not already installed: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Note**: Model setup:
- **ACE-Step**: Infrastructure is ready. Configure model checkpoint via `ACE_STEP_MODEL_PATH` environment variable if needed
- **SongGeneration**: Requires cloned repository and runtime files (see main README for details)
- **Mistral**: Automatically downloads from HuggingFace on first use

### 2. Set Up Backend

```bash
cd ../backend
# Install uv if not already installed: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Set Up Frontend

```bash
cd ../frontend
npm install
```

## Running the Application

### Terminal 1: Model Service
```bash
cd model-service
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Terminal 2: Backend API
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

## Access the Application

- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Model Service Docs: http://localhost:8001/docs

## Using Docker Compose

Alternatively, use Docker Compose to run all services:

```bash
docker-compose up
```

## Testing the Application

1. Open http://localhost:5173 in your browser
2. Fill in the form:
   - Select a music style (required)
   - Optionally add topic, refrain, or complete text
   - Set duration (10-300 seconds)
   - Choose number of versions (1-5)
3. Click "Generate Music"
4. Wait for generation to complete
5. Select and play versions, or download them

## Troubleshooting

- **Port already in use**: Change ports in the respective service configurations
- **Model service not responding**: Ensure model service is running on port 8001
- **CORS errors**: Check backend CORS settings in `backend/app/main.py`
- **Module not found**: Ensure virtual environments are activated and dependencies are installed

## Next Steps

- Integrate actual ACE-Step model (see `model-service/app/models/ace_step.py`)
- Configure model path via `ACE_STEP_MODEL_PATH` environment variable
- Customize styles and generation parameters
- Add authentication if needed
- Set up production deployment

