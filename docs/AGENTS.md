# AGENTS.md

## Layout

- `LiveEditBackend/` — Flask API + Celery workers. `app.py` is a large monolith (auth gate, routes, DB, schema init); async work lives in `video_tasks.py`, `video_ingestion.py`, and `video_director.py`.
- `LiveEditFronten/` — React 19 + TypeScript + Vite SPA. The directory name is misspelled in the repo; use it as-is.
- `docs/` — notes on past fixes; `DEPLOYMENT.md` describes the Cloud Run + Firebase flow used by `deploy.sh`.
- There is a root `package-lock.json` but no root `package.json`; run npm commands inside `LiveEditFronten/`.

## Run locally

- Frontend: `cd LiveEditFronten && npm install && npm run dev` → http://localhost:3000. The README's 5173 is stale; Logto redirects also assume 3000.
- Backend: from the repo root, `./start-backend.sh` starts local Redis (if needed), a Celery worker, and Flask on :5000. To run separately: `cd LiveEditBackend`, then `./start-celery.sh` and `python app.py`.
- Async routes (`/api/analyze-video`, `/api/edit-video`, `/api/edit-multi`) need Redis + the Celery worker; without them jobs stay `queued`.
- Keep heavy work in Celery tasks. Request handlers should enqueue and return `202` with a `job_id`.
- API and worker must share `DATABASE_URL` and `JOB_WORKDIR` (default `/tmp/liveedit_jobs`); media blobs live in Postgres, temp files on disk.

## Environment

- `LiveEditBackend/.env` must define `DATABASE_URL`; `app.py` raises at import without it. Importing the app also runs `init_*` table creation, which only logs warnings on failure.
- `python init_db.py` creates/seeds `audio_effects` (that table is not created by app startup).
- AI defaults to Vertex AI (`USE_VERTEX_AI=true`), requiring `VERTEX_PROJECT_ID` and Google credentials. For key-based local use set `USE_VERTEX_AI=false` and `GEMINI_API_KEY`.
- Frontend config: `VITE_BACKEND_URL` (falls back to `VITE_API_URL`), `VITE_LOGTO_ENDPOINT`, `VITE_LOGTO_APP_ID`, and `VITE_GEMINI_API_KEY` for direct browser Gemini calls. Any `VITE_*` value is public in the bundle.
- Every `/api/*` route requires `Authorization: Bearer <Logto ID token>` via `app.before_request`, except `GET /api/payments/plans`. `/health` is public. CORS origins are hardcoded defaults plus `FRONTEND_URL` / `FRONTEND_URLS`.

## Tests and verification

- Backend tests are in `LiveEditBackend/tests/`; run from `LiveEditBackend`: `pytest` (or `pytest -k <name>`). Install pytest first — it is not in `requirements.txt`: `pip install pytest pytest-cov`.
- Backend tests import `app`, so `DATABASE_URL` must be set; they monkeypatch `app.verify_logto_token` and `app.get_db_connection` so no real auth/database is used.
- CI (`.github/workflows/tests.yml`) runs backend tests with `--cov-fail-under=70` from `LiveEditBackend`.
- The frontend has **no test runner**: `package.json` only defines `dev`, `build`, `preview`, and `npm test` fails with "Missing script". README, `TESTING.md`, `__tests__/example.test.tsx`, and the CI frontend job are stale/aspirational on this point.
- Verify frontend changes with `npm run build` (Vite only; it does not typecheck). `npx tsc --noEmit` currently reports numerous pre-existing errors, including in `__tests__/` and several components/services, so it is not a clean gate.
- No lint, formatter, or typecheck scripts/config exist for either app.
