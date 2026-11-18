# Codex / AI Agent Instructions — Reunify

## Mission
Build a synthetic-data-only disaster-reunification MVP. Families submit missing-person details; hospitals submit unidentified patient details; authorized reviewers receive ranked candidate evidence and independently verify identity. AI must NEVER mark an identity verified or automatically contact families.

## Target architecture
- `frontend/` Next.js, TypeScript, Tailwind CSS
- `backend/` FastAPI, Pydantic, SQLAlchemy, SQLite for local demo
- Future modules: `backend/app/services/ai/face_matching.py` (DeepFace+ArcFace) and `clothing_detection.py` (Grounding DINO). Do not pull weights or activate by default. Model/checkpoint licenses must be checked.
- Later probabilistic matching (Splink) should combine visual evidence with name, age, physical description, location and timeline; support *no match*.

## Mandatory guardrails
- Work only with synthetic/consented demo images. Do not commit patient photographs, embeddings, private contacts, secrets, weights, or database files.
- Family accounts cannot view hospital records or match candidates. Require authentication and access controls before implementing restricted endpoints.
- Face distances and garment detections are uncertain evidence, not verified identity.
- Distinguish 'not detected' from 'absent'. Multiple people in one image require person-association before scoring clothes.
- Keep mock results explicitly labeled and never substitute a fake result silently for inference errors.
- Do not expose medical or biometric data in URLs, API errors, logs, telemetry or public build artifacts.

## Work process
Read `docs/BUILD_CHECKLIST.md` and `docs/ORIGINAL_PROMPT.md` before starting a new work session or resuming after context compaction. The checklist records current progress; the original prompt preserves the user's requirements. Update the checklist with evidence when an item is completed, and include links to both documents in each completion report. Mark implemented, tested, pushed, and merged states separately; do not mark placeholders or mock inference as completed real functionality.

1. Read this file and README before changing code.
2. Implement one phase at a time. For Phase 1, make dashboard + backend API + local seed data work.
3. Run available tests and typecheck; write a small test for each backend behavior.
4. Commit small, meaningful changes on a feature branch and open a pull request with a summary and test results. Never force-push to protected `main`.
5. Do not assume changes are auto-committed. Explicitly check git status, commit and push (when authorized).

## Upcoming phases
1. Foundations (current): structure, incident dashboard, seed data and API health.
2. Authenticated, restricted intake forms + image storage interface.
3. Optional face-comparison and clothing-detection inference services with negative/uncertain outcomes.
4. Probabilistic matching + reviewer evidence panels.
5. Human decision workflow + immutable audit trail.
6. Evaluation and pitch demo.

## Data and evaluation
Synthetic data from Synthea/FEBRL/Splink only in appropriate license terms; split training/test by person and incident, measure recall@5, false-match rates, score calibration and reviewer burden. Public demo uses generated scenario counts only.
