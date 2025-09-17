# Repository Guidelines

## Project Structure & Modules
- `backend/app/`: FastAPI service (entry: `main.py`), domain modules (`calculator.py`, `efatura_parser.py`, exports, validators).
- `backend/requirements.txt`: backend Python deps; `.env.example` for config.
- `backend/uploads/`, `backend/temp/`: runtime data (ignored); do not commit artifacts.
- `frontend/`: static UI (`index.html`, `improvements.js`, `advanced_charts.js`).
- Root: helper scripts, sample data, and system tests (`test_*.py`), docs (`README.md`, plans).

## Build, Test, and Development
- Setup (Python 3.10+):
  - `cd backend && python -m venv venv && source venv/bin/activate`
  - `pip install -r requirements.txt`
- Run API (dev):
  - `cd backend && uvicorn app.main:app --reload` (or `cd backend/app && uvicorn main:app --reload`)
- Open UI: `frontend/index.html` (optionally `cd frontend && python -m http.server 8080`).
- Tests (API must be running):
  - `python test_efatura_endpoint.py`
  - `python test_complete_system.py`
  - Additional utilities under `backend/test_*.py` for data checks.

## Coding Style & Naming
- Python: PEP 8, 4-space indent, snake_case for files/functions, PascalCase for classes. Keep modules cohesive and pure where possible.
- JavaScript: camelCase for vars/functions; keep DOM/logic separated in `improvements.js` and charts in `advanced_charts.js`.
- Files: tests start with `test_...py`; avoid committing large binaries; prefer `.json` or small samples.

## Testing Guidelines
- Favor small, reproducible samples; place ad-hoc fixtures alongside the test script or under `backend/temp/` (gitignored).
- Validate endpoints at `http://localhost:8000`; prefer the end-to-end script `test_complete_system.py` when changing API contracts.
- If adding tests, mirror the existing script style and name `test_<area>.py`.

## Commit & Pull Requests
- Commit messages: short, imperative. Prefer Conventional Commit prefixes (`feat:`, `fix:`, `chore:`) when reasonable.
- PRs must include: problem statement, summary of changes, test evidence (logs or screenshots), and any config updates (`.env.example`). Link issues when available.

## Security & Configuration
- Never commit secrets. Copy `.env.example` to `.env` locally and document new keys.
- Uploads and temp data are ephemeral; sanitize filenames and user data in logs.
