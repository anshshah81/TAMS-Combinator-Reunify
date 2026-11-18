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

Not implemented in Phase 1: authentication, intake, uploads, or patient access.

## Phase 2 — Authentication and intake

Implemented: development-only demo authentication (fictional seeded accounts),
role-aware navigation, a public landing page, the family missing-person form, the
hospital unidentified-patient form, authorized image upload/retrieval with
validation and metadata stripping, and authenticated family report tracking that
never reveals patient records or candidate matches. The dashboard now lives at
`/dashboard`; `/` is the landing page.

Server-side access control is authoritative: family accounts create and view only
their own reports; hospital accounts create and view only their own organization's
patients; reviewers and administrators may read patient records. Mutations require a
same-origin custom header (CSRF defense). Demo authentication is NOT production
security — it only turns on when `APP_ENV=development` and `DEMO_AUTH_ENABLED=true`,
and is refused otherwise.

Still placeholders pending later phases: `/matches` (review) and `/admin`. No AI
inference, reviewer decisions, notifications, or model weights exist yet.

### Enabling the demo portal

From `backend/`, after `alembic upgrade head` and `python -m app.seed`:

```powershell
$env:APP_ENV = 'development'
$env:DEMO_AUTH_ENABLED = 'true'
.venv/Scripts/python -m app.seed_accounts
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

With demo auth disabled (the default), every restricted route denies access and the
public dashboard still works. Uploaded images are written to a gitignored `uploads/`
directory (override with `UPLOAD_DIR`); they are never served from a public path.

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

The public overview and incident list count only seeded scenario records (by id
prefix), so authenticated demo intake never changes the public totals.

### Restricted API (Phase 2)

Requires development-only demo authentication; disabled by default. Credentialed
CORS is limited to `http://localhost:3000` and mutations require the
`x-reunify-csrf` header. These are demo safeguards, not production security.

- `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`,
  `GET /api/v1/auth/demo-accounts`.
- `POST /api/v1/reports`, `GET /api/v1/reports`, `GET /api/v1/reports/{id}/tracking`
  (family; own records only).
- `POST /api/v1/patients`, `GET /api/v1/patients`, `GET /api/v1/patients/{id}`
  (hospital own organization; reviewer/admin read).
- `POST /api/v1/images`, `GET /api/v1/images/{id}` (authorized upload and retrieval).

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
CORS, deny-by-default restricted routes, demo auth sessions (login/expiry/revocation),
role/organization/ownership isolation, CSRF, image upload bounds and authorization,
duplicate internal ids, and consent backfill from Phase 1 rows. CI runs Python
3.11/3.12 backend checks and Node 22 frontend lint, typecheck, and production build
without AI weights.

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
