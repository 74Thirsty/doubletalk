# DoubleTalk / VantageChatbot - production Dockerfile
# Usage (API):
#   docker build -t doubletalk .
#   docker run --env-file .env -p 8000:8000 doubletalk
#
# Usage (Worker):
#   docker run --env-file .env doubletalk celery -A src.jobs.celeryApp.celeryApp worker -l INFO
#
# Assumptions:
# - Your FastAPI app is exposed as: src.main:app  (change if different)
# - Your Celery app object is: src.jobs.celeryApp.celeryApp (change if different)

FROM python:3.11.8-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

WORKDIR /app

# Minimal OS deps (safe defaults for common py wheels + git deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
  && rm -rf /var/lib/apt/lists/*

# Install deps first (better build cache)
COPY requirements.txt ./
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir -r requirements.txt

# Copy only the project pieces you actually need in the image
COPY src/ ./src/
COPY tests/ ./tests/
COPY pytest.ini ./
COPY alembic.ini ./
COPY README.md ./
# If you use alembic migrations in-code, keep them:
COPY src/storage/migrations/ ./src/storage/migrations/

EXPOSE 8000

# Default: run the API
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
