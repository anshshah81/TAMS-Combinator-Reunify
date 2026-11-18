# Reunify build checklist

Updated: 2026-11-17. Requirements: [original user prompt](ORIGINAL_PROMPT.md).
This checklist uses the master prompt's seven build phases, which split the broader
AI and review milestones in AGENTS.md into smaller deliverables.

## Resume here

- Current implementation: Phase 2 authentication and intake, on `feature/backend-intake-workflows`.
- Foundation commit: `dd34c2a934ae7ab9f167e1f32715d75ff40e5e84` (Phase 1, on `main`).
- Phase 2 adds development-only demo auth, family/hospital intake, image storage, and family
  tracking. Demo auth is off by default and refuses to run outside development.
- Next implementation: Phase 3 facial similarity (mock + opt-in ArcFace), no real verification.
- No real AI inference, reviewer workflow, or deployment exists yet.
- Keep the existing starter directory; do not move or overwrite teammates' work.

## How to keep context

1. Read this checklist, the original prompt, AGENTS.md, and README before resuming.
2. Inspect working-tree changes, remote main, recent commits, and open PRs.
3. Work in phase order. Check an item only after implementing and verifying it.
4. Record the relevant tests, commit, branch, PR, and merge state in the ledger below.
5. After each completed item, send the user the checklist and original-prompt links,
   newly completed items, next items, and blockers. Include a compact phase checklist.
6. Preserve ORIGINAL_PROMPT.md verbatim. Record later scope decisions here rather
   than rewriting the historical request. These files survive chat compaction;
   links do not guarantee that their full text stays in the model's context.

## Non-negotiable requirements throughout

- Synthetic/consented demonstrations only; never commit patient photos, contacts,
  medical records, embeddings, databases, secrets, or model weights.
- AI supplies uncertain evidence, never verified identity or automatic family contact.
- Family accounts must never see patient records or candidate matches.
- Restricted APIs require authentication, role, organization, and ownership checks.
- Label mocks explicitly; never silently substitute them when inference fails.
- Distinguish non-detection from absence; associate garments with the target person.
- Keep medical/biometric data out of URLs, errors, logs, telemetry, and build output.
- Use feature branches, meaningful commits, tests, and reviewed PRs; no force-pushes
  to main or automatic merges of major features.

## Phase 1 — Foundation

- [x] Preserve and inspect the starter, README, and AGENTS.md.
- [x] Authenticate as `anshshah81` and configure GitHub no-reply commit identity.
- [x] Publish public `anshshah81/TAMS-Combinator-Reunify`, default branch `main`.
- [x] Scaffold Next.js App Router, React, TypeScript, Tailwind, and Lucide navigation.
- [x] Scaffold versioned FastAPI API and generated OpenAPI docs.
- [x] Set up SQLAlchemy, SQLite, initial indexes, and Alembic migration.
- [x] Add explicit, repeatable synthetic seed data without images or contacts.
- [x] Connect dashboard to API with six exercise counts.
- [x] Add incident search/status filters and loading, error, retry, and empty states.
- [x] Add health endpoint and public synthetic incident/overview endpoints.
- [x] Keep later workflow routes visibly labeled as placeholders.
- [x] Add 21 isolated backend tests, including migration round trips and absent restricted routes.
- [x] Add frontend lint, typecheck, production build, and npm lockfile.
- [x] Pin direct dependencies and keep heavy AI packages out of standard installation.
- [x] Add environment examples, ignore rules, startup/demo/team documentation, and PR template.
- [x] Add CI for Python 3.11/3.12 and Node 22; verify successful GitHub runs.
- [x] Protect main: passing checks, up-to-date branches, one review, stale-review dismissal,
  conversation resolution, no force pushes or deletions, administrator enforcement.
- [x] Commit and publish the functional foundation.

## Phase 2 — Authentication and intake workflows

- [x] Add User and Organization models, relationships, indexes, and migrations.
- [x] Implement explicit development-only fictional authentication, disabled outside demo use.
- [x] Enforce family, hospital, reviewer, and administrator roles on the server.
- [x] Enforce organization scopes and report ownership; test cross-role/cross-user denial.
- [x] Add portal login/session handling and role-aware navigation; label demo auth honestly.
- [x] Build landing page with branding, mission, matching explanation, report and staff actions.
- [x] Establish reusable UI components consistent with the existing frontend.
  Note: hand-rolled Tailwind primitives (`components/ui.tsx`) following shadcn/ui
  conventions, chosen over the shadcn CLI to avoid new dependencies and keep the
  locked frontend install and CI stable.
- [x] Build missing-person form: name/nickname, approximate age, height, hair/eye color,
  distinguishing features, last-known place/time, clothing, photo, reporter contact, consent.
- [x] Build hospital intake: hospital/internal identifier, estimated age/height, hair/eye
  color, distinguishing features, clothing, intake place/time, authorized photo.
- [x] Support unknown/missing patient attributes without inventing values.
- [x] Implement input validation, timezone handling, persistence, and schema migrations.
- [x] Add secure image-storage abstraction and authenticated upload/retrieval boundaries.
- [x] Validate image content/format/size; use opaque identifiers and safe storage paths.
- [x] Provide submission success/error states and a report tracking ID.
- [x] Add authenticated family tracking with limited status and no hospital/candidate disclosure.
- [x] Test forms, persistence, invalid inputs, uploads, access restrictions, and failure states.
  Backend: 22 Phase 2 tests in `tests/test_intake.py`. Frontend verified via lint/typecheck/build;
  no frontend unit tests yet.
- [ ] Commit `feat: implement family and hospital intake workflows`; push and open PR.

## Phase 3 — Facial similarity

- [x] Create `backend/app/services/ai/face_matching.py` with a structured comparison contract.
- [x] Implement explicitly labeled mock and opt-in real DeepFace/ArcFace adapters.
- [x] Separate optional inference dependencies and pin compatible versions.
  Note: `backend/requirements-ai.txt` separates them; versions are intentionally
  left unpinned there with a rationale (platform/Python/GPU-dependent) and must be
  pinned in a verified locked environment before real use.
- [x] Review and document code, detector, model/checkpoint licenses before enabling weights.
  See [AI model licensing](ai_model_licensing.md).
- [x] Validate input images and handle missing, unusable, unsupported, and no-face cases.
- [x] Reject ambiguous multi-face comparisons unless safe explicit selection is implemented.
  The real adapter returns a distinct `ambiguous_faces` status; the mock performs no detection.
- [x] Detect/align faces, generate embeddings, and return cosine distance plus metadata.
  Real adapter only; the default mock returns a clearly labeled pseudo-distance.
- [x] Record model/detector versions/configuration and warnings; do not claim a calibrated
  identity probability or use an unvalidated threshold as independent verification.
- [x] Protect the comparison endpoint and keep embeddings/photos out of source and logs.
- [x] Test positive/error/uncertain paths without downloading weights in ordinary CI.
- [ ] Commit `feat: integrate ArcFace facial similarity service`; push and open PR.

## Phase 4 — Clothing detection

- [ ] Create `backend/app/services/ai/clothing_detection.py` with mock and opt-in real adapters.
- [ ] Validate Grounding DINO code/checkpoint licensing and optional dependency compatibility.
- [ ] Validate images and description inputs; prepare text prompts and run detection.
- [ ] Return garment phrases, normalized/documented boxes, scores, query support, and metadata.
- [ ] Distinguish failed detection, non-detection, obscuration, and possibly changed clothing.
- [ ] Avoid assuming detected garment category confirms its color.
- [ ] Require person association for multi-person images before clothing contributes evidence.
- [ ] Add restricted detection endpoint and reviewer bounding-box visualization.
- [ ] Test detections, failures, ambiguous people, no detections, and presentation.
- [ ] Commit `feat: integrate Grounding DINO clothing detection`; push and open PR.

## Phase 5 — Record matching

- [ ] Create `backend/app/services/ai/match_engine.py` and restricted matching API.
- [ ] Implement transparent candidate retrieval with incident/location/timeline constraints.
- [ ] Combine available face, clothing, age, height, name/nickname, distinguishing-feature,
  location, and timeline evidence without treating missing data as disagreement.
- [ ] Persist supporting, conflicting, and missing evidence, model versions, ranking score,
  and review status for every candidate.
- [ ] Support no sufficiently supported candidate; do not force a match.
- [ ] Keep rank scores distinct from calibrated identity probabilities.
- [ ] Evaluate Splink as a probabilistic baseline; document licensing and evaluation result.
- [ ] Test supported, conflicting, incomplete, and no-match cases; prevent record leakage.
- [ ] Commit `feat: implement AI-assisted candidate matching`; push and open PR.

## Phase 6 — Investigation and human review

- [ ] Build restricted AI match dashboard with report/patient IDs, face/clothing evidence,
  other evidence, conflicts/missing data, review status, and investigation action.
- [ ] Build side-by-side investigation view with authorized photos, attributes, boxes,
  face evidence, timestamps, and reviewer notes.
- [ ] Add Investigate Further and Request Additional Information actions.
- [ ] Add Reject Candidate with reasons and appropriate status transitions.
- [ ] Add Record Independent Identity Verification with required human evidence/attestation.
- [ ] Prevent AI/matching execution from setting verified status or contacting families.
- [ ] Complete ReviewDecision and AuditLog relationships, migrations, and immutable audit trail.
- [ ] Add authorized admin incident management, user/organization permissions, and audit access.
- [ ] Update family status through a restricted projection that reveals no candidate/patient details.
- [ ] Test permissions, concurrent/invalid transitions, audit integrity, and verification prerequisites.
- [ ] Commit `feat: implement case review and resolution workflow`; push and open PR.

## Phase 7 — Evaluation and competition demo

- [ ] Create complete fictional scenario spanning intake, suggestions, no match, review, and resolution.
- [ ] Document synthetic dataset provenance/license terms (Synthea/FEBRL/Splink where applicable).
- [ ] Split evaluation data by person and incident to prevent leakage.
- [ ] Measure recall@5, false-match rates, calibration where applicable, and reviewer burden.
- [ ] Document actual measured performance and limitations; do not invent accuracy claims.
- [ ] Verify end-to-end role workflows and privacy boundaries.
- [ ] Complete responsive/accessibility checks and loading/error/empty states across all pages.
- [ ] Resolve remaining applicable dependency findings and failing checks before deployment.
- [ ] Write full pitch/demo instructions, limitations, and team startup/onboarding guide.
- [ ] Obtain team's intended licensing terms before adding any LICENSE file.
- [ ] Invite both teammates once their GitHub usernames are supplied and verify acceptance.
- [ ] Commit `chore: prepare Reunify competition MVP`; push and open PR.

## Evidence ledger

| Deliverable | State | Evidence |
| --- | --- | --- |
| Phase 1 foundation | Implemented, tested, published on main | Commit `dd34c2a934ae7ab9f167e1f32715d75ff40e5e84`; 21 backend tests; lint/typecheck/build passed; browser search and empty filtering verified |
| Hosted CI | Passed | [Main CI run](https://github.com/anshshah81/TAMS-Combinator-Reunify/actions/runs/44216979353), Python 3.11/3.12 and frontend successful |
| GitHub collaboration documentation | Implemented and pushed; PR open, not merged | Commit `fe8e651`, branch `docs/github-publishing`, [PR #1](https://github.com/anshshah81/TAMS-Combinator-Reunify/pull/1); CI passed |
| Continuity checklist and original prompt | Implemented and validated; tracked on `docs/mvp-build-checklist` | Documentation-only; original prompt byte-for-byte equality and local document links verified; publication/PR reported in chat |
| Phase 2 auth + intake | Implemented and tested on `feature/backend-intake-workflows` | Migration `d9b4ba78b25b`; commit `424dac7`; 39 backend tests; `pip check`/`alembic check` clean; frontend lint/typecheck/build pass; live HTTP login/report/overview/CSRF flow verified |
| Phase 3 facial similarity | Implemented and tested on `feature/ai-face-matching` | Mock + opt-in ArcFace adapters; protected `/api/v1/face-comparisons`; 46 backend tests pass with no weight downloads; licensing documented |
| Phases 4–7 | Not implemented | Clothing detection, matching, reviewer workflow, and demo evaluation not yet built |

## Open constraints and decisions

- Full npm audit reports 13 high-severity development-tool entries associated with
  picomatch; production dependency audit reported zero. See [dependency notes](dependencies.md).
- No team license or model/checkpoint approval exists; do not imply otherwise.
- No teammate usernames have been supplied for invitations.
- Development-only authentication must precede any restricted endpoint.
- Cloud deployment, real medical use, and automatic family notification are not authorized.
