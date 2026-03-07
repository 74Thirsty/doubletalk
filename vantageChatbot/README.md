# Vantage Chatbot

FastAPI chatbot backend with Telegram/Messenger webhook adapters, deterministic domain handlers (FAQ/scheduling/orders/handoff), Celery reminder worker, and an integrated browser chat client served from `/`.

## Architecture

- **API server:** `src/app.py` (FastAPI, SQLAlchemy models, admin routes, webhook routes, web chat route).
- **Domains:**
  - `src/domains/info`: FAQ + business info responses.
  - `src/domains/scheduling`: appointment booking + reminder row creation.
  - `src/domains/orders`: simple product order flow.
  - `src/domains/customerService`: human handoff ticketing.
- **Storage:** SQLAlchemy models in `src/storage/models.py`; default local SQLite DB (`vantagechatbot.db`) unless `DATABASE_URL` is set.
- **Async jobs:** Celery app + reminder task (`src/jobs/`).
- **Frontend:** static SPA in `frontend/`, mounted by FastAPI at `/`.

---

## Prerequisites

- Python 3.10+
- Optional for full infra mode: Docker + Docker Compose

---

## Local setup (single-process, SQLite)

```bash
cd vantageChatbot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set environment variables (override defaults only when needed):

```bash
export DATABASE_URL="sqlite:///./vantagechatbot.db"
export ADMIN_API_KEY="adminkey"
export CORS_ALLOW_ORIGINS="*"
```

Run API + frontend:

```bash
PYTHONPATH=. uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

The web client is now available at `http://localhost:8000/`.

---

## Seed data (required before meaningful chat flows)

All admin routes require `X-Admin-Key: $ADMIN_API_KEY`.

```bash
# 1) Create tenant
curl -s -X POST http://localhost:8000/admin/tenants \
  -H 'content-type: application/json' \
  -H "X-Admin-Key: $ADMIN_API_KEY" \
  -d '{"name":"Demo Tenant","timezone":"UTC"}'

# 2) Add a service for scheduling flow
curl -s -X POST http://localhost:8000/admin/services \
  -H 'content-type: application/json' \
  -H "X-Admin-Key: $ADMIN_API_KEY" \
  -d '{"tenant_id":1,"name":"Haircut","duration_min":30,"price_cents":2500}'

# 3) Add a product for order flow
curl -s -X POST http://localhost:8000/admin/products \
  -H 'content-type: application/json' \
  -H "X-Admin-Key: $ADMIN_API_KEY" \
  -d '{"tenant_id":1,"name":"Pizza","sku":"PIZZA-01","price_cents":1599}'

# 4) Add FAQ for info flow
curl -s -X POST http://localhost:8000/admin/faqs \
  -H 'content-type: application/json' \
  -H "X-Admin-Key: $ADMIN_API_KEY" \
  -d '{"tenant_id":1,"question":"refund","answer":"Refunds are supported within 7 days."}'
```

---

## Use the web client (full-stack path)

1. Open `http://localhost:8000/`.
2. Set **Tenant ID** (`1` if you used the seed commands above).
3. Send sample prompts:
   - `refund` → FAQ path.
   - `book appointment` then `yes` → scheduling + appointment/reminders DB writes.
   - `order pizza` then `yes` → order + order item writes.
   - `human` → customer service ticket flow.

The client sends `POST /api/chat` requests and renders replies in chat history.

---

## API surfaces

### Health
- `GET /healthz`
- `GET /readyz`

### Admin
- `POST /admin/tenants`
- `POST /admin/services`
- `POST /admin/products`
- `POST /admin/faqs`

### Web chat
- `POST /api/chat`
  - body: `{ "tenant_id": 1, "text": "refund", "session_id": "uuid" }`

### Webhooks
- Telegram: `POST /webhooks/telegram/{tenant_id}`
- Messenger verify: `GET /webhooks/messenger/{tenant_id}`
- Messenger events: `POST /webhooks/messenger/{tenant_id}`

---

## Docker setup (Postgres + Redis + API + worker + beat)

```bash
cd vantageChatbot/docker
docker compose up --build
```

Notes:
- Compose uses `.env.example` as `env_file`. Update it or swap to `.env` if needed.
- Ensure `DATABASE_URL` points to postgres service (`postgresql+psycopg2://postgres:postgres@postgres:5432/vantagechatbot`).
- API is exposed on `http://localhost:8000`.

---

## Tests

```bash
cd vantageChatbot
PYTHONPATH=. pytest
```

---

## Operational notes

- Idempotency is enforced on `(tenant_id, channel_type, provider_message_id)` for inbound messages.
- `ADMIN_API_KEY` is env-driven; do not hardcode in production.
- For non-local deployments, restrict CORS (`CORS_ALLOW_ORIGINS`) instead of `*`.
- Current state machine is stateless per message (`ConversationState()` initialized per request). Extend if you need multi-turn persistence semantics.
