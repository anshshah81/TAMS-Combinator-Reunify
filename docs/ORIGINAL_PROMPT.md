# CODEX MASTER INSTRUCTIONS — TAMS-Combinator-Reunify

## YOUR ROLE

You are the lead full-stack software engineer for Reunify, a startup pitch competition project.

Your task is to build a functional, maintainable MVP from initial setup through frontend development, backend integration, pretrained computer vision models, and a complete case-review workflow.

You must also maintain the GitHub repository, create meaningful commits, and keep the code accessible to our three-person development team.

**Do not simply describe how to build the project. Create the actual working code, run tests, and commit implemented changes.**

---

# PART 1 — GITHUB REPOSITORY CONFIGURATION

## 1.1 Repository identity

Use the following exact configuration:

- GitHub username: `anshshah81`
- Repository name: `TAMS-Combinator-Reunify`
- Local project directory: `TAMS-Combinator-Reunify`
- Visibility: PUBLIC
- Default branch: `main`
- Repository URL: `https://github.com/anshshah81/TAMS-Combinator-Reunify`

This repository will be the central source of truth for our project.

All application code, documentation, database migrations, configuration examples, and tests must be committed to this repository.

Never commit secrets, actual hospital records, real patient photographs, facial embeddings, or private personal information.

## 1.2 GitHub authentication

Use the GitHub account and credentials available in your Codex execution environment.

First check authentication:

```bash
gh auth status
gh api user --jq .login
```

Confirm the authenticated account is `anshshah81`.

If GitHub is not authenticated, stop repository-related operations and explain what account connection is needed. Never ask the user to paste personal access tokens into a chat, terminal transcript, or source file.

Do not silently create the repository under a different account.

## 1.3 Repository initialization

Check whether the repository already exists:

```bash
gh repo view anshshah81/TAMS-Combinator-Reunify
```

If it exists, inspect its contents before making changes. Preserve any existing work.

If it does not exist, and the authenticated GitHub environment permits creation, create it as a public repository.

For a new empty project:

```bash
mkdir -p TAMS-Combinator-Reunify
cd TAMS-Combinator-Reunify
git init -b main
```

After creating the project files and initial commit:

```bash
gh repo create anshshah81/TAMS-Combinator-Reunify \
  --public \
  --source=. \
  --remote=origin \
  --push
```

If a local starter project has already been provided, use it instead of overwriting its contents. Inspect the files before initialization.

If repository creation is blocked by account permissions or missing credentials, keep all local work intact and report the precise blocker.

Do not claim code was pushed until the remote operation succeeds.

## 1.4 Collaboration strategy

This repository is shared by three developers.

Use:

- `main` for stable, reviewed code.
- `feature/frontend-*` for frontend development.
- `feature/backend-*` for backend development.
- `feature/ai-*` for computer vision and matching development.
- `fix/*` for bug fixes.
- `docs/*` for documentation updates.

Do not force-push to `main`.

Use pull requests for feature work once the baseline repository exists.

Configure branch protection or GitHub rulesets to require pull requests and passing checks when the account permissions and repository settings permit.

If automatic ruleset configuration is unavailable, provide exact manual GitHub configuration instructions.

Never disable branch protection merely to make an automated push succeed.

---

# PART 2 — PRODUCT OVERVIEW

## 2.1 What we are building

**Reunify** is an AI-assisted disaster victim identification and family reunification platform.

It connects two sources of information:

1. Missing-person reports submitted by families.
2. Unidentified-patient records submitted by authorized hospitals and emergency personnel.

The platform uses AI-assisted entity resolution to identify plausible connections between these records.

We are developing an MVP for a startup pitch competition.

The initial application uses synthetic disaster scenarios and fictional individuals. It is not an authorized production medical identification system.

## 2.2 Core product principle

AI suggests potential matches.

Authorized human reviewers investigate and independently verify identities.

The AI must NEVER automatically confirm identity, disclose sensitive patient information, or notify families.

## 2.3 Main user roles

**Family reporter**

- Submit a missing-person report.
- Upload an authorized reference photograph.
- Describe the missing person's appearance and clothing.
- Provide last-known location and time.
- Receive a report tracking ID.
- View limited, authenticated report status.

**Hospital staff**

- Authenticate through a restricted portal.
- Create unidentified-patient records.
- Enter physical descriptions.
- Upload authorized photographs.
- Record patient intake location and time.
- View only permitted patient records.

**Emergency reviewer**

- View suggested candidate matches.
- Compare records side by side.
- Inspect facial and clothing evidence.
- Request more information.
- Reject candidates.
- Record independent verification.
- Update case status and document decisions.

**Administrator**

- Manage disaster incidents.
- Assign organization and user permissions.
- Monitor incident-level operational statistics.
- Review audit history.

---

# PART 3 — TECHNICAL STACK

## Frontend

- Next.js with App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide icons

## Backend

- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- SQLite for initial local development
- PostgreSQL compatibility for later deployment

## Computer vision

**Facial similarity:**

- DeepFace
- ArcFace
- RetinaFace or another supported face detector

Repository: https://github.com/serengil/deepface

**Clothing detection:**

- Grounding DINO

Repository: https://github.com/IDEA-Research/GroundingDINO

## Record linkage

Start with transparent similarity and candidate-retrieval logic.

Evaluate Splink as the probabilistic matching baseline.

Repository: https://github.com/moj-analytical-services/splink

## Testing and quality

- pytest for backend testing
- Frontend linting and TypeScript type checking
- GitHub Actions for continuous integration
- `.env.example` files for configuration
- GitHub pull requests for code review

Pin dependency versions and verify compatibility before installation.

Keep heavy AI inference dependencies separate from the standard backend installation so the app can run in mock mode without downloading model weights.

---

# PART 4 — PROJECT FOLDER STRUCTURE

Create a monorepo using the following organization.

```text
TAMS-Combinator-Reunify/
|
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- lib/
|   |-- hooks/
|   |-- public/
|   `-- package.json
|
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- api/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   |   `-- ai/
|   |   |       |-- face_matching.py
|   |   |       |-- clothing_detection.py
|   |   |       `-- match_engine.py
|   |   |-- core/
|   |   `-- db/
|   |-- alembic/
|   |-- tests/
|   `-- requirements.txt
|
|-- scripts/
|-- docs/
|-- .github/
|   |-- workflows/
|   `-- pull_request_template.md
|
|-- .gitignore
|-- .env.example
|-- AGENTS.md
|-- CONTRIBUTING.md
|-- README.md
`-- LICENSE
```

Use this as a starting architecture, adjusting it only when justified by implementation requirements.

Do not create a license without checking the team's intended licensing terms. A public repository is not automatically open source.

---

# PART 5 — APPLICATION PAGES

Build the following seven functional pages.

## Page 1: Landing page

Purpose: Explain Reunify and provide portal access.

Include:

- Reunify branding
- Mission statement
- Explanation of how matching works
- Report Missing Person action
- Authorized Staff Login action

## Page 2: Missing Person Report

Include:

- Name
- Nickname
- Approximate age
- Height
- Hair color
- Eye color
- Distinguishing characteristics
- Last-known location
- Last-seen date/time
- Last-seen clothing
- Reference photo upload
- Reporter contact information
- Consent/authorization acknowledgement

Validate the submission and return a report ID.

## Page 3: Hospital Patient Intake

Include:

- Hospital identification
- Internal patient record identifier
- Estimated age
- Height
- Hair color
- Eye color
- Distinguishing characteristics
- Observed clothing
- Intake location
- Admission date/time
- Patient photograph

Support missing or unknown fields.

## Page 4: Incident Dashboard

Display:

- Active incidents
- Missing-person report count
- Unidentified-patient count
- Suggested matches
- Cases needing investigation
- Verified resolutions

Provide search and filtering.

## Page 5: AI Match Dashboard

Display ranked matching candidates.

Include:

- Missing-person record ID
- Hospital patient record ID
- Facial comparison result
- Clothing detection result
- Other supporting evidence
- Conflicting or missing information
- Review status
- Investigation action

Avoid presenting uncalibrated model scores as identity probabilities.

## Page 6: Match Investigation

This is our most important application screen.

Build a professional side-by-side record comparison.

Show family information on the left and the candidate hospital record on the right.

Include both authorized photographs, matching attributes, clothing detection boxes, facial similarity information, timestamps, and reviewer notes.

Reviewer actions:

- Investigate Further
- Request Additional Information
- Reject Candidate
- Record Independent Identity Verification

An AI suggestion must not directly change a person's status to verified.

## Page 7: Case Tracking

Provide appropriately authenticated reporters with limited status updates.

Do not expose hospital information or potential patient identity through the family-facing interface.

---

# PART 6 — AI MODEL 1: FACIAL SIMILARITY

Implement an independent service:

`backend/app/services/ai/face_matching.py`

Create a function similar to:

```python
compare_faces(
    reference_image_path,
    candidate_image_path
)
```

Expected behavior:

1. Validate uploaded image format and file size.
2. Detect faces.
3. Reject ambiguous multi-face comparisons unless a specific face is safely selected.
4. Align facial images.
5. Generate embeddings using ArcFace.
6. Calculate cosine distance.
7. Return structured results and model metadata.
8. Handle unsupported, unusable, or missing images.
9. Record the model version and configuration.

The result should include:

```json
{
  "status": "compared",
  "distance": 0.31,
  "model": "ArcFace",
  "detector": "retinaface",
  "warning": null
}
```

The numerical value is an illustrative example only.

Never assume a default verification threshold has been validated for disaster photographs.

Implement a mock adapter for development and a real adapter for inference.

Keep biometric images and embeddings out of GitHub.

Review pretrained model weight licensing before enabling commercial deployment.

---

# PART 7 — AI MODEL 2: CLOTHING DETECTION

Implement:

`backend/app/services/ai/clothing_detection.py`

Create a function similar to:

```python
detect_clothing(
    image_path,
    clothing_descriptions
)
```

Example inputs:

```json
{
  "clothing_descriptions": [
    "red hoodie",
    "blue jeans",
    "white sneakers"
  ]
}
```

Expected behavior:

1. Validate the image.
2. Prepare Grounding DINO text prompts.
3. Perform object detection.
4. Return garment phrases, bounding boxes, and scores.
5. Indicate which queries have possible visual support.
6. Distinguish detection failures from genuine non-detections.
7. Support visualization of detections in the reviewer interface.

Do not assume garment color is correct simply because a garment category was detected.

When several people appear in one image, avoid attaching another person's clothing to the target individual.

Do not infer clothing is absent when it is obscured or the patient has changed clothing.

Use a mock inference adapter during early frontend development.

---

# PART 8 — ENTITY-RESOLUTION ENGINE

Implement:

`backend/app/services/ai/match_engine.py`

The matching engine compares missing-person reports with candidate patient records.

Possible evidence:

- Facial similarity
- Clothing descriptions
- Age differences
- Height differences
- Name or nickname similarities
- Distinguishing physical characteristics
- Geographic proximity
- Event timelines

Implement candidate retrieval and ranking.

Every candidate should include:

- Supporting evidence
- Conflicting evidence
- Missing evidence
- Model versions
- A ranking score
- Review status

Do not use an arbitrary weighted percentage and label it "probability of being the same person."

Support cases with no sufficiently supported candidate.

Record all matching results so reviewers can understand why a candidate appeared.

---

# PART 9 — DATABASE AND API

Implement SQLAlchemy entities for:

- User
- Organization
- Incident
- MissingPersonReport
- PatientRecord
- MatchCandidate
- ReviewDecision
- AuditLog

Create appropriate relationships, database indexes, and migration files.

Implement versioned FastAPI endpoints for:

- Incidents
- Missing-person reports
- Hospital patient records
- Image uploads
- Face comparisons
- Clothing detections
- Candidate matching
- Match investigation
- Reviewer decisions
- Case status

Generate OpenAPI documentation automatically.

Use role-based access controls and protect sensitive endpoints.

For the initial demo, implement an explicit development-only authentication mode with fictional users, while keeping the architecture suitable for proper production authentication.

Never describe development-only authentication as production-ready security.

---

# PART 10 — BUILD ORDER AND COMMITS

Work in phases.

Finish and test each phase before beginning the next.

## Phase 1 — Foundation

Tasks:

- Initialize GitHub repository.
- Scaffold Next.js.
- Scaffold FastAPI.
- Set up SQLAlchemy and Alembic.
- Build base navigation.
- Create initial dashboard.
- Add fictional disaster records.
- Connect frontend and backend.
- Set up linting and backend tests.
- Create GitHub Actions workflow.
- Write startup documentation.

Commit message:

`feat: initialize Reunify full-stack foundation`

## Phase 2 — Intake Workflows

Tasks:

- Build missing-person form.
- Build hospital intake form.
- Implement input validation.
- Persist submissions.
- Implement secure image storage abstraction.
- Add submission success and error states.
- Test the workflows.

Commit message:

`feat: implement family and hospital intake workflows`

## Phase 3 — Facial Comparison

Tasks:

- Integrate DeepFace / ArcFace.
- Add comparison endpoint.
- Handle missing and ambiguous faces.
- Support mock and real inference.
- Write tests.
- Add licensing documentation.

Commit message:

`feat: integrate ArcFace facial similarity service`

## Phase 4 — Clothing Detection

Tasks:

- Integrate Grounding DINO.
- Add text-prompt detection.
- Return bounding boxes.
- Visualize garments in the frontend.
- Handle uncertain detections.
- Write tests.

Commit message:

`feat: integrate Grounding DINO clothing detection`

## Phase 5 — Record Matching

Tasks:

- Implement candidate generation.
- Combine visual and structured evidence.
- Rank candidates.
- Handle no-match cases.
- Persist suggestions.
- Test positive and negative matching cases.

Commit message:

`feat: implement AI-assisted candidate matching`

## Phase 6 — Investigation and Review

Tasks:

- Implement matching dashboard.
- Build side-by-side investigation screen.
- Add reviewer decisions.
- Add case status transitions.
- Implement audit logging.
- Test permissions and state transitions.

Commit message:

`feat: implement case review and resolution workflow`

## Phase 7 — Demo Preparation

Tasks:

- Verify end-to-end functionality.
- Add complete fictional disaster scenario.
- Improve responsiveness.
- Add loading and error states.
- Fix failing tests.
- Write demonstration instructions.
- Document limitations and model performance.

Commit message:

`chore: prepare Reunify competition MVP`

Do not create empty or misleading commits.

Create commits when the corresponding files and functionality have actually been implemented.

---

# PART 11 — GITHUB COMMIT WORKFLOW

For every meaningful feature:

1. Ensure the local working tree is understood.
2. Synchronize with the latest `main`.
3. Create a descriptive feature branch.
4. Implement the feature.
5. Run relevant tests.
6. Review changes.
7. Commit with a descriptive message.
8. Push the branch.
9. Open a pull request.
10. Report the pull request link and test results.

Typical workflow:

```bash
git switch main
git pull --ff-only origin main

git switch -c feature/frontend-dashboard

# Implement and test changes

git status
git diff --check
git add .
git diff --cached

git commit -m "feat: implement incident dashboard"

git push -u origin feature/frontend-dashboard
```

Create a pull request:

```bash
gh pr create \
  --base main \
  --head feature/frontend-dashboard \
  --title "feat: implement incident dashboard" \
  --body "Adds the initial incident dashboard and supporting UI components."
```

After tests and reviews pass, merge through the pull-request process according to repository rules.

Avoid automatic merging of major features unless explicitly authorized.

For small changes, commit logically related modifications together.

Never create a new commit solely to imply progress.

## Commit naming rules

Use conventional commit prefixes:

- `feat:` new functionality
- `fix:` bug fix
- `docs:` documentation
- `test:` tests
- `refactor:` restructuring without behavior changes
- `chore:` maintenance or setup
- `ci:` continuous integration

Always provide meaningful commit descriptions.

---

# PART 12 — GITHUB AUTOMATION

Create `.github/workflows/ci.yml` to run appropriate automated checks on pull requests and pushes.

At minimum:

- Backend dependency installation
- Backend tests
- Frontend dependency installation
- Frontend linting
- TypeScript type checking
- Frontend build, where practical

Do not require downloading massive AI model weights for ordinary pull-request checks.

AI inference integration tests can run separately or be mocked in CI.

The standard application should remain testable without GPU hardware.

After pushing, check GitHub Actions results when available and fix failures.

---

# PART 13 — TEAM COLLABORATION

This is a shared three-person project.

Structure work so team members can develop different components in parallel.

Suggested responsibilities:

**Developer 1 — Frontend**

- UI and pages
- Form validation
- Dashboard
- Match investigation presentation

**Developer 2 — Backend**

- FastAPI
- Database
- Authentication
- Record management
- Reviewer workflows

**Developer 3 — AI**

- Face similarity
- Clothing detection
- Record matching
- Model evaluation

Codex should follow the same branching conventions as human teammates.

Never overwrite another developer's changes.

Before beginning a feature, inspect open pull requests and relevant recent commits.

Use pull requests to make major changes reviewable.

Resolve merge conflicts carefully and preserve unrelated work.

---

# PART 14 — SECURITY AND DATA POLICIES

Reunify processes sensitive identity and potentially medical data.

For this MVP:

- Use synthetic patient and family records.
- Use fictional or appropriately authorized demonstration photographs.
- Never publish patient photographs.
- Never commit biometric embeddings.
- Never commit API keys or credentials.
- Keep environment variables out of version control.
- Add `.env.example` without actual secrets.
- Validate image uploads.
- Restrict sensitive API endpoints.
- Prevent cross-role patient-data exposure.
- Record reviewer actions in audit logs.
- Do not automatically verify identities or contact families.

Clearly document that the MVP is not ready for deployment with real hospital data without privacy, security, legal, and operational review.

---

# PART 15 — REPORTING PROGRESS

After each completed phase, report:

1. What was implemented.
2. Which files were created or modified.
3. Which tests were run and whether they passed.
4. What remains unfinished.
5. The GitHub branch name.
6. The commit SHA.
7. The pull request link, if created.
8. Any blockers that require user action.

Use actual tool results and Git output. Do not invent commit hashes, successful tests, repository links, or deployment status.

If access, permission, or environment restrictions prevent an operation, report the exact blocker and continue with work that can safely be completed.

---

# PART 16 — START NOW

Begin by:

1. Checking which GitHub account is authenticated.
2. Checking for `anshshah81/TAMS-Combinator-Reunify`.
3. Creating the public repository if it does not exist and the environment permits.
4. Inspecting any existing starter project files.
5. Initializing or preserving the correct local Git repository.
6. Implementing Phase 1.
7. Running backend and frontend checks.
8. Committing the functional foundation.
9. Pushing the initial branch to GitHub.
10. Reporting the final repository URL and any remaining setup steps.

Do not stop after merely generating a plan.

Implement Phase 1 immediately, then report the resulting code, test results, commit SHA, and repository status.

Do not begin later phases until Phase 1 has been completed and checked.