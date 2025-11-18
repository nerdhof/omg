# Model Service

Microservice for running music generation models. Supports multiple providers: ACE-Step and Tencent SongGeneration.

## Setup

1. Install dependencies using uv:
```bash
# Install uv if not already installed: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

This will create a virtual environment (`.venv`) and install all dependencies from `pyproject.toml`.

2. Configure music generation provider:
   - The service supports two providers: `ace-step` (default) and `song-generation`
   - Set `MUSIC_PROVIDER` environment variable to choose the default provider
   - For ACE-Step: Model will be automatically downloaded from GitHub on first use
   - For SongGeneration: Model will be automatically downloaded from Hugging Face on first use

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

### General Configuration
- `MODEL_SERVICE_PORT`: Port to run on (default: 8001)
- `DEVICE`: Device to use ('cpu', 'cuda', or 'mps' for Apple devices, default: 'cpu')
- `MUSIC_PROVIDER`: Default music generation provider (default: 'ace-step')
  - Options: `ace-step`, `song-generation`

### ACE-Step Configuration
- `ACE_STEP_MODEL_PATH`: Path to local model checkpoint (optional, overrides default)

### SongGeneration Configuration (LeVo SongGeneration)

**Important**: LeVo SongGeneration requires the official repository to be set up. It's not a simple Hugging Face model that can be loaded directly.

#### Setup Steps:

1. **Clone the official repository:**
   ```bash
   git clone https://github.com/tencent-ailab/SongGeneration.git
   cd SongGeneration
   ```

2. **Install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # On Windows: .venv\Scripts\activate

   pip install -r requirements.txt
   pip install -r requirements_nodeps.txt --no-deps
   ```

3. **Install Git LFS and pull large files:**
   ```bash
   # Install Git LFS if not already installed
   git lfs install
   
   # Pull the actual large files (not just pointers)
   git lfs pull
   ```
   
   **Important**: The repository uses Git LFS for large files like `tools/new_prompt.pt`. 
   Without pulling these files, you'll get "invalid load key" errors.

4. **Download runtime files:**
   ```bash
   huggingface-cli download lglg666/SongGeneration-Runtime --local-dir ./runtime
   mv runtime/ckpt ckpt
   mv runtime/third_party third_party
   ```

5. **Download model checkpoint:**
   ```bash
   # Choose one of these models:
   huggingface-cli download lglg666/SongGeneration-base --local-dir ./songgeneration_base
   # OR
   huggingface-cli download lglg666/SongGeneration-base-new --local-dir ./songgeneration_base_new
   # OR
   huggingface-cli download lglg666/SongGeneration-base-full --local-dir ./songgeneration_base_full
   # OR
   huggingface-cli download lglg666/SongGeneration-large --local-dir ./songgeneration_large
   ```

6. **Set environment variables:**
   ```bash
   export SONG_GENERATION_REPO_PATH=/path/to/SongGeneration
   export SONG_GENERATION_MODEL_ID=lglg666/SongGeneration-base  # or the model you downloaded
   ```

#### Environment Variables:
- `SONG_GENERATION_REPO_PATH`: Path to the cloned SongGeneration repository (required)
- `SONG_GENERATION_MODEL_ID`: Hugging Face model ID or local checkpoint path (default: "lglg666/SongGeneration-base")
  - Available models:
    - `lglg666/SongGeneration-base` (default)
    - `lglg666/SongGeneration-base-new` (2m30s, zh/en, 10G/16G GPU)
    - `lglg666/SongGeneration-base-full` (4m30s, zh/en, 12G/18G GPU)
    - `lglg666/SongGeneration-large` (4m30s, zh/en, 22G/28G GPU)

#### Additional Resources:
- Official repository: https://github.com/tencent-ailab/SongGeneration
- Demo page: https://levo-demo.github.io/
- Hugging Face models: https://huggingface.co/lglg666

## How It Works

The service supports multiple music generation providers:

1. **ACE-Step**: Uses the ACE-Step pipeline from GitHub
2. **SongGeneration**: Uses Tencent's SongGeneration model from Hugging Face

### Provider Selection

You can choose which provider to use in three ways:

1. **Environment Variable** (default): Set `MUSIC_PROVIDER` to `ace-step` or `song-generation`
2. **API Endpoint**: Use `POST /model/v1/provider/switch` to switch providers dynamically
3. **Per-Request Override**: Include `provider` field in the generation request to use a specific provider for that request

### Resource Management

- Only one provider's model is loaded in memory at a time
- When switching providers, the previous provider's resources are automatically cleaned up
- GPU memory is cleared when switching providers (if using CUDA)

## API Endpoints

### Music Generation
- `POST /model/v1/generate`: Generate music from text prompt
  - Optional `provider` field to override default provider for this request
- `GET /model/v1/generate/{job_id}/status`: Get generation job status
- `GET /model/v1/generate/{job_id}/progress`: Get generation job progress
- `DELETE /model/v1/generate/{job_id}/cancel`: Cancel a generation job

### Provider Management
- `GET /model/v1/provider`: Get current provider and available providers
- `POST /model/v1/provider/switch`: Switch to a different provider
- `GET /model/v1/provider/status`: Get status information for all providers

### Health & Info
- `GET /health`: Health check and current provider information

### Lyrics Generation
- `POST /model/v1/lyrics/generate`: Generate or refine lyrics

### Generate Music Example

```bash
# Generate with default provider
curl -X POST "http://localhost:8001/model/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A soothing classical piano piece",
    "duration": 10.0,
    "num_versions": 1
  }'

# Generate with specific provider (per-request override)
curl -X POST "http://localhost:8001/model/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A soothing classical piano piece",
    "duration": 10.0,
    "num_versions": 1,
    "provider": "song-generation"
  }'
```

### Switch Provider Example

```bash
# Switch to SongGeneration
curl -X POST "http://localhost:8001/model/v1/provider/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "song-generation"
  }'

# Get current provider
curl "http://localhost:8001/model/v1/provider"

# Get provider status
curl "http://localhost:8001/model/v1/provider/status"
```

See `/docs` for interactive API documentation.

