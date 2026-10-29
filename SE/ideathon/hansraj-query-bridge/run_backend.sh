#!/usr/bin/env bash
# Starts the API on http://127.0.0.1:8000 (creates venv, installs deps, auto-creates DB + demo data).
set -e
cd "$(dirname "$0")/backend"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
