# Reunify — TAMS-Combinator-Reunify

Synthetic-data-only disaster-reunification foundation for a three-person pitch team.
AI may suggest evidence; only authorized humans may independently verify identity.
This is a local demonstration, not an operational medical identification system.

## Phase 1

Project continuity: [live build checklist](docs/BUILD_CHECKLIST.md) and
[original user prompt, preserved verbatim](docs/ORIGINAL_PROMPT.md).

Implemented: Next.js App Router dashboard and navigation, six scenario totals,
incident search/status filters, loading/error/retry/empty states, FastAPI public
exercise API, SQLAlchemy models, Alembic migration, explicit fictional seed data,
isolated tests, and GitHub Actions checks. Existing starter work is preserved in
this folder; cloning the published repository will use `TAMS-Combinator-Reunify`.

Not implemented: authentication, intake, uploads, AI inference, reviewer actions,
notifications, or patient access. `/report`, `/hospital`, `/matches`, `/tracking`,
and `/admin` are clearly labeled placeholders. No model weights are installed.
The internal starter case models are scaffolding, not secured operational storage.

## Requirements

Python 3.11 or 3.12, Node.js 22, npm 10, and Git. Direct dependencies are pinned;
`frontend/package-lock.json` locks the frontend dependency tree. Backend transitive
dependencies are resolved by pip. SQLite is the tested local database; PostgreSQL
needs a driver, configuration, and integration testing before use.

## Run locally — Windows PowerShell

Backend, from the repository root:

```powershell
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/alembic upgrade head
.venv/Scripts/python -m app.seed
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend, in another terminal from the repository root:

```powershell
cd frontend
npm ci
Copy-Item .env.local.example .env.local
npm run dev
```

Open http://localhost:3000. API docs: http://localhost:8000/docs.
On macOS/Linux, use `python3 -m venv .venv`, `.venv/bin/python`,
`.venv/bin/alembic`, and `cp .env.local.example .env.local` instead.

Migrations and seeding are explicit; starting the API does not change the database.
Seed only an empty demo database. Repeated seeding preserves existing records and
skips databases already containing an incident. The seed contains two fictional
incidents (one active, one closed), two reports, two patients, one mock candidate,
and zero verified resolutions. No photographs, embeddings, or contact details.

The default database is `backend/reunify_demo.sqlite3`, ignored by Git. To override,
set the process variable `$env:DATABASE_URL = 'sqlite:///another_demo.sqlite3'`
from `backend/` before migrating, seeding, or starting the API. Python does not
automatically load `.env` files. Never point this demo at operational data.
If an old starter database already exists without migration history, preserve it
and use a fresh demo database path; do not stamp an unverified schema as migrated.

## Public API

- `GET /api/v1/health`: service liveness, with `demo_only: true`.
- `GET /api/v1/incidents`: synthetic incident metadata, optionally `q` (name/region,
  maximum 100 characters) and `status=active|closed`. No case details.
- `GET /api/v1/demo/overview`: generated scenario counts across all exercises;
  `incident_count` counts active incidents. `suggested_matches` includes the seeded
  mock candidate, not an inference result or probability.

CORS permits the local frontend at `http://localhost:3000`. It is not authentication.
No sensitive routes are exposed. Authentication, organization scoping, and ownership
checks must precede Phase 2 intake and case APIs.

## Checks

```powershell
cd backend
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m pip check
.venv/Scripts/alembic check
```

```powershell
cd frontend
npm ci
npm run lint
npm run typecheck
npm run build
```

Backend tests migrate temporary databases and cover health, exact totals, filtering,
validation, empty data, seed preservation/idempotence, migration upgrade/downgrade,
CORS, and the absence of restricted routes. CI runs Python 3.11/3.12 backend checks
and Node 22 frontend lint, typecheck, and production build without AI weights.

## Team and repository

Intended public repository: https://github.com/anshshah81/TAMS-Combinator-Reunify.
See [GitHub setup](docs/github-setup.md) for publishing and branch protection.
Use `feature/frontend-*`, `feature/backend-*`, `feature/ai-*`, `fix/*`, and `docs/*`
branches. Review and merge through PRs; never force-push `main`.
See [CONTRIBUTING.md](CONTRIBUTING.md) and [demo instructions](docs/demo.md).

## License and limitations

No open-source license is granted until the team chooses terms. Public visibility
alone is not a license. Pretrained model/checkpoint licenses have not been approved;
DeepFace, ArcFace, Grounding DINO, and Splink remain future work. No performance or
accuracy claim has been measured. Never submit real medical, biometric, or contact
data. Real deployment requires privacy, security, legal, and operational review.

Dependency audit details and the remaining development-tooling advisory are recorded
in [docs/dependencies.md](docs/dependencies.md).
