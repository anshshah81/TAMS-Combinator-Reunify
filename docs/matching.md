# Candidate matching

Reunify's matching engine (`backend/app/services/ai/match_engine.py`) compares a
missing-person report against unidentified-patient records within the same incident
and produces ranked candidates for human review.

## What it does

For each report/patient pair it records explicit:

- Supporting evidence (e.g. close age, matching hair color, overlapping clothing).
- Conflicting evidence (e.g. age differs by 15+ years, mismatched hair color).
- Missing evidence (fields absent on either record, or comparisons not run).

The ranking score is a transparent tally: `len(supporting) - len(conflicting)`.

## What it is NOT

- The ranking score is **not** a probability that two records are the same person.
- Thresholds (age, height, face distance) are heuristic defaults for ordering only;
  they are not validated identity criteria and must be calibrated on licensed,
  consented data before any real use.
- Missing information is recorded as missing, never counted as disagreement.
- Clothing overlap is weak evidence because clothing changes; a detected garment
  category does not confirm color. Facial distance is uncertain evidence only.
- The engine supports a "no confident match" outcome: when nothing is supported,
  no candidate is produced. A match is never forced.
- Generating candidates never sets a verified status and never contacts anyone.

Every candidate persists its evidence (`evidence_json`), the engine version, the
ranking score, and a review status, so a reviewer can see exactly why a candidate
appeared.

## Splink evaluation (baseline)

[Splink](https://github.com/moj-analytical-services/splink) (MIT License) is the
intended probabilistic record-linkage baseline. It uses the Fellegi-Sunter model to
estimate match weights and can combine structured fields (age, height, descriptors,
location, timeline) with visual evidence as additional comparison features.

Status: evaluated as a baseline design, not yet integrated. A calibrated Splink
model requires labeled training pairs split by person and incident to avoid leakage,
which depends on a licensed synthetic dataset (Phase 7). Until then, Reunify ships
the transparent heuristic above so reviewers are never shown an uncalibrated
probability. When Splink is integrated, its output must remain labeled as a model
estimate and continue to feed human review rather than any automated verification.
