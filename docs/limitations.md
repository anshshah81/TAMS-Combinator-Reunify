# Limitations and responsible-use notes

Reunify is an early MVP for a pitch competition. It is **not** a medical device,
not a production system, and not authorized for real disaster or clinical use.

## What it does not do

- It does **not** confirm identity. Only a human reviewer can record a verification,
  and only with a written attestation of independent evidence.
- It does **not** contact families automatically. Resolution only updates a coarse,
  detail-free status on the family's own report.
- It does **not** produce calibrated probabilities. The ranking score is a
  transparent evidence tally for ordering suggestions, nothing more.
- It does **not** use real data. All records, accounts, and images are synthetic or
  explicitly consented demo content.

## Known technical limitations

- **AI is uncertain evidence.** Facial distance and clothing detection are weak
  signals. A non-detection means "not detected", not "absent". Clothing changes and
  a detected garment category does not confirm its color.
- **Multi-person images** require person association before clothing contributes
  evidence; the detection result always carries that warning.
- **Real inference is off by default.** Face matching and clothing detection run as
  clearly labeled mocks; the real adapters are opt-in, unpinned, and require model
  and checkpoint license review before use (see [AI model licensing](ai_model_licensing.md)).
- **Reviewer burden is high.** On synthetic evaluation the engine surfaces ~20
  candidates per report to avoid missing true matches; top-1 is unreliable
  (~13% wrong). See [evaluation](evaluation.md).
- **Evaluation is synthetic only.** Measured numbers describe a generated
  distribution and do not predict real-world accuracy.
- **Demo authentication** is development-only, disabled by default, and refuses to
  run outside development. It is not a real account system.

## Operational guardrails

- Never commit real photographs, biometric embeddings, medical records, private
  contacts, secrets, model weights, or database files.
- Keep medical and biometric data out of URLs, errors, logs, telemetry, and build
  artifacts.
- Family accounts can never see hospital records or candidate matches.
- Audit entries are append-only and store only actor, action, and record id.
