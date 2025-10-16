Backend launcher

This folder provides a stable entry-point to run the existing API without changing the current code structure.

- The FastAPI application still lives under `app/` (e.g., `app/main.py`).
- These launchers simply import and run `app.main:app`.

Quick start

```bash
# From repo root
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python backend/start.py
```

Or use the shell script:

```bash
bash backend/start.sh
```

Environment variables are loaded from `.env` at the repo root via `app/config.py`.


