#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "./.venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


