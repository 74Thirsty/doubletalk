#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 -m http.server 4173 &
PYTHONPATH=. uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

