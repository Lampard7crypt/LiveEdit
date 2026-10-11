# Copilot instructions for LiveEdit

## Repository shape

LiveEdit is a full-stack AI video editor with two independently run apps:

- `LiveEditBackend/` is the Flask API. `app.py` centralizes routes and persistence
  for auth, payments, media uploads, video jobs, ingestion, and the director flow.
  Backend modules are flat-imported (for example `from ai_client import ...`), so
  commands should be run from `LiveEditBackend` or with the virtualenv activated.
- `LiveEditFronten/` is a React 19 + TypeScript + Vite app. `App.tsx` routes the
  authenticated/landing/projects/editor flows; reusable UI goes in `components/`,
  shared data shapes live in `types.ts`, and API calls live in `services/`.

The main runtime path is: frontend service/component -> Flask `/api/*` route ->
PostgreSQL and/or a Gemini/Vertex/Redis integration. Video work is asynchronous:
Flask stores job metadata and uploaded files, queues Celery tasks, and the frontend
polls `/api/video-jobs/<job_id>`. `video_ingestion.py` and `video_director.py`
handle AI scene analysis, structured edit plans, and rendering; `ai_client.py`
selects the active backend (Vertex by default, Gemini Developer API when
`USE_VERTEX_AI=false`).

Authentication uses Logto with Google social sign-in. The frontend sends Logto
ID tokens as Bearer tokens; Flask validates them and provisions a local user
keyed by Logto ID. See `docs/LOGTO_AUTH.md` for required environment
configuration and the verified-email legacy account-linking behavior.

## Build, test, and validation commands

### Initial setup

From the repo root:

```bash
./setup.sh
```

Manual setup:

```bash
cd LiveEditBackend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../LiveEditFronten
npm install
```

Backend config is read from `LiveEditBackend/.env` or environment variables. The
backend expects `DATABASE_URL`; Vertex-based video flows also need Google Cloud
application credentials, `VERTEX_PROJECT_ID`, and `GCS_BUCKET_NAME`. Do not
commit `.env` files or credentials.

### Run locally

Use separate terminals:

```bash
# API
cd LiveEditBackend
source venv/bin/activate
python app.py

# Celery worker
cd LiveEditBackend
./start-celery.sh

# Frontend
cd LiveEditFronten
npm run dev
```

The frontend dev server runs on port 5173; the backend is on port 5000. When the
API is not local, set `VITE_BACKEND_URL` or `VITE_API_URL` in the frontend env.
`start-backend.sh` can start Redis, Celery, and Flask together when Redis is
installed locally.

### Validation commands

Use targeted validation before broad runs:

```bash
# Backend full suite
cd LiveEditBackend
source venv/bin/activate
pytest -v

# Single backend file
cd LiveEditBackend && pytest tests/test_analysis_cache.py -v

# Single backend test case
cd LiveEditBackend && pytest tests/test_analysis_cache.py::TestCacheStatsEndpoint::test_stats_without_redis -v

# Keyword selection
cd LiveEditBackend && pytest -k "chat" -v

# Coverage gate used by CI
cd LiveEditBackend && pytest --cov=. --cov-report=term-missing --cov-fail-under=70 -v

# Frontend build validation
cd LiveEditFronten && npm run build
```

Important: there is no lint script in `LiveEditFronten/package.json`, and the repo
currently does not define a working `npm test` setup. Treat `npm test` as
unavailable unless the frontend test tooling is explicitly added as part of the
change. The existing example frontend test is under `LiveEditFronten/__tests__/`.

Smoke test while the backend is running:

```bash
curl http://localhost:5000/health
```

## High-level architecture and workflow

- Frontend state and screen transitions are organized around `AppMode`; keep mode
  changes explicit and centralised rather than spreading UI flow into ad-hoc flags.
- Backend routes in `app.py` are the entrypoints for all user-facing AI operations.
  If a task touches AI generation, media processing, billing, or auth, prefer the
  existing route/task flow over introducing a browser-only implementation.
- Redis + Celery powers async video jobs. The status/result payloads returned by the
  job endpoints are part of the contract used by the frontend; preserve field names
  when changing `video_tasks.py` or the job API response shapes.
- Video ingestion is a multi-stage pipeline: upload, queue job, analyze/transform,
  store job output, and poll for completion. Keep uploaded-job temp files compatible
  with both the Flask process and the Celery worker.
- `ai_client.py` is the source of truth for model selection and AI backend
  configuration. Reuse `get_genai_client()` and the model accessors instead of
  constructing a new client or reading keys directly in each module.

## Key conventions specific to this repo

- Load configuration through environment variables and the existing `python-dotenv`
  setup. Vertex mode uses ADC via `GOOGLE_APPLICATION_CREDENTIALS`; Gemini Developer
  API mode uses `GEMINI_API_KEY`.
- Backend tests should patch module-level collaborators used by the route/task, such
  as `ai_client.get_genai_client`, `app.get_db_connection`, Celery `.delay`, or
  `video_tasks._redis_client`. Do not make real Gemini, Redis, database, or cloud
  calls from tests.
- Analysis caching is opt-in via `ENABLE_ANALYSIS_CACHE`, uses Redis keys prefixed
  with `liveedit:analysis:`, tracks hit/miss counters, and supports the
  `skip_cache` request parameter. Preserve the bypass behavior when Redis is absent.
- Multipart video upload handling needs the existing secure filename and workspace/db
  helpers; do not bypass those utilities with ad-hoc save paths.
- Frontend API interfaces should stay consistent with the shared service style and
  backend URL normalization. Keep response/error handling aligned with the existing
  service functions.
- Data structures shared across components belong in `LiveEditFronten/types.ts`.
  Endpoint-specific request/response types should stay next to the service that owns
  that API flow.
- Gemini video generation in `services/gemini.ts` is a direct browser SDK flow, but
  chat, editing, ingestion, director, payment, auth, and subscription logic should
  remain server-side. Do not silently move a backend-controlled workflow to the
  browser, especially if it relies on credentials or media processing.
- Preserve deployment assumptions: backend is suitable for Gunicorn/Cloud Run,
  frontend builds to Vite `dist/` and deploys to Firebase/Vercel, and production
  media uses GCS, Vertex AI, PostgreSQL, and Redis.

## Working guidance for future sessions

- Prefer small, targeted changes and validate with the smallest relevant test/build.
- When editing AI or cache code, preserve the existing status/result fields and cache
  metadata, and keep the "skip cache when Redis is unavailable" behavior intact.
- When changing routes or async tasks, keep the API contract stable for the polling
  frontend and the job-status endpoints.
- For database work, prefer the existing `get_db_connection()`/workspace helpers over
  creating a second persistence path.

## Authoritative references

- `README.md`: quick start and product overview
- `CONTRIBUTING.md`: local setup and contribution workflow
- `TESTING.md`: test layout and expected commands
- `ARCHITECTURE_DIAGRAM.md`: high-level service relationships
- `DEPLOYMENT.md`: production environment assumptions
- `docs/`: project-specific fixes and workflow notes

## Optional browser verification

When Playwright is available in the Copilot host, use it for front-end flows that
need a real browser rather than ad-hoc manual scripts. Start the frontend, backend,
and Celery worker as needed, then verify the relevant UI path through the browser.
Keep API keys and production credentials out of browser-session config; use local
environment variables and the existing Vite/backend URL settings.
