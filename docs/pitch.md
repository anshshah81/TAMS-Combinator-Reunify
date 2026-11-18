# Pitch and demo guide

## The problem

After a disaster, families search for missing loved ones while hospitals admit
unidentified patients. Reconciling the two is slow, manual, and error-prone, and
mistakes in identification are devastating. Sensitive medical and biometric data
makes naive automation dangerous.

## Our approach

Reunify is an **AI-assisted, human-decided** reunification platform. AI narrows a
large search space and explains its reasoning with transparent evidence; authorized
human reviewers investigate side by side and independently verify identity. The
system never confirms an identity or contacts a family on its own.

## Why it is safe

- Synthetic/consented data only; strict role and organization boundaries.
- AI output is labeled uncertain evidence, never verified identity.
- Human-only verification requires a written attestation; every decision is written
  to an immutable audit trail.
- Mocks are labeled and never silently substituted for real inference.

See [limitations](limitations.md) for the full responsible-use notes.

## Live demo (5 minutes)

Enable the development-only demo portal (README), then follow the full
[end-to-end scenario](scenario.md):

1. **Family** files a synthetic missing-person report and sees a tracking status.
2. **Hospital** records an unidentified patient (unknown fields left blank).
3. **Reviewer** generates ranked candidates with transparent evidence, shows a
   **no-match** case, investigates side by side, and runs the mock face/clothing
   tools (labeled uncertain).
4. **Reviewer** records a verification with an attestation; family status becomes a
   coarse "resolved" with no details.
5. **Admin** shows the immutable audit trail.

## Evidence it works

- 69 backend tests and passing frontend lint/typecheck/build.
- Reproducible synthetic evaluation: recall@5 = 1.0, top-1 false-match 13.3%,
  reviewer burden ~19.6 candidates/report (see [evaluation](evaluation.md)).

## Team onboarding

1. Read `AGENTS.md`, `README.md`, this guide, and [BUILD_CHECKLIST](BUILD_CHECKLIST.md).
2. Set up the backend and frontend per the README; run migrations and seed demo data.
3. Enable the demo portal only in development (`APP_ENV=development`, `DEMO_AUTH_ENABLED=true`).
4. Backend: `cd backend; pytest`. Frontend: `cd frontend; npm run lint; npx tsc --noEmit; npm run build`.
5. Evaluation: `cd backend; python -m app.eval.evaluate_matching`.
6. Work on feature branches, keep commits small, and open PRs; never force-push to
   `main`. Collaboration details are in [GitHub setup](github-setup.md).
7. See [dataset provenance](dataset.md) before adding any data.

## Roadmap beyond the MVP

- Opt-in real face matching (ArcFace) and clothing detection (Grounding DINO) after
  license review and a pinned, verified environment.
- Probabilistic linkage with Splink, kept as a labeled model estimate feeding human
  review — never automated verification.
- Reduce reviewer burden with a learned threshold and calibrated scoring.
