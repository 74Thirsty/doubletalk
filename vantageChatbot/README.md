# Vantage Chatbot

Production-oriented omni-channel customer service bot scaffold using FastAPI + PostgreSQL/Redis-ready architecture.

## Features

- Telegram and Messenger webhook adapters normalized into one core `InboundMessage` model.
- Deterministic workflows for scheduling, reminders, orders, FAQ, and human handoff.
- Admin API with API-key protection for tenant/service/product/FAQ config.
- Idempotent inbound processing via provider message ID persistence.
- Celery task hooks for reminder dispatch with retries.

## Project layout

Matches the required structure under `src/`, `tests/`, and `docker/`.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn src.app:app --reload
```

## Run tests

```bash
PYTHONPATH=. pytest tests
```

## Docker

```bash
cd docker
docker compose up --build
```

## Webhook endpoints

- Telegram: `POST /webhooks/telegram/{tenant_id}`
- Messenger verify: `GET /webhooks/messenger/{tenant_id}`
- Messenger events: `POST /webhooks/messenger/{tenant_id}`

## Admin API

Requires `X-Admin-Key` header.

- `POST /admin/tenants`
- `POST /admin/services`
- `POST /admin/products`
- `POST /admin/faqs`

## Reliability notes

- Duplicate provider IDs are ignored.
- Reminder task includes automatic backoff retries.
- Appointments and orders are DB-backed and committed atomically in handlers.
