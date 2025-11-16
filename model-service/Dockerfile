FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies (ffmpeg required for ACE-Step, build tools for compiling packages)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project configuration
COPY pyproject.toml uv.lock .

# Install Python dependencies with uv sync
RUN uv sync --no-editable

# Copy application code (needed for editable install)
COPY app/ ./app/

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

