# Frontend (Web Chat Client)

Static browser client for exercising the backend conversational flows through `POST /api/chat`.

## Run modes

### Recommended: served by FastAPI

Run backend from repo root:

```bash
PYTHONPATH=. uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

Then open <http://localhost:8000>.

### Standalone static hosting

```bash
cd frontend
python3 -m http.server 4173
```

Then open <http://localhost:4173> and set **API Base URL** to your backend origin (for example `http://localhost:8000`).

## Usage

1. Set tenant ID.
2. Send messages from the composer.
3. Reset session to rotate the synthetic user ID (`session_id`) used by backend idempotent persistence.
