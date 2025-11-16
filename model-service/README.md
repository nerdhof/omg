# Model Service

Microservice for running music generation models using ACE-Step with diffusers.

## Setup

1. Install dependencies using uv:
```bash
# Install uv if not already installed: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

This will create a virtual environment (`.venv`) and install all dependencies from `pyproject.toml`.

2. Configure ACE-Step model:
   - The service uses ACE-Step from Hugging Face by default
   - Model will be automatically downloaded from Hugging Face on first use
   - You can override the model ID using `ACE_STEP_MODEL_ID` environment variable

## Running

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Or with Docker:
```bash
docker build -t model-service .
docker run -p 8001:8001 model-service
```

## Environment Variables

- `MODEL_SERVICE_PORT`: Port to run on (default: 8001)
- `ACE_STEP_MODEL_ID`: Hugging Face model ID (default: "ACE-Step/ACE-Step-v1-3.5B")
  - Options: "ACE-Step/ACE-Step-v1-3.5B", "ACE-Step/ACE-Step"
- `DEVICE`: Device to use ('cpu', 'cuda', or 'mps' for Apple devices, default: 'cpu')
- `ACE_STEP_MODEL_PATH`: Path to local model checkpoint (optional, overrides model ID)

## How It Works

The service uses `diffusers` library to load and run ACE-Step:

1. On startup, the model is initialized using `DiffusionPipeline.from_pretrained("ACE-Step/ACE-Step-v1-3.5B", dtype=torch.bfloat16, device_map="cuda")`
2. The pipeline automatically handles model loading, preprocessing, and inference
3. Generated audio is saved as WAV files and returned via the API

## API Endpoints

- `GET /health`: Health check and model information
- `POST /model/v1/generate`: Generate music from text prompt

### Generate Music Example

```bash
curl -X POST "http://localhost:8001/model/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A soothing classical piano piece",
    "duration": 10.0,
    "num_versions": 1
  }'
```

See `/docs` for interactive API documentation.

