# AI model and checkpoint licensing

Reunify treats AI output as uncertain evidence for human reviewers, never as
identity verification. The standard install runs labeled mock adapters only. Real
inference is opt-in via `backend/requirements-ai.txt` and must not be enabled for
any commercial or production use before the licenses below are reviewed and
approved by the team. No model weights are committed to this repository.

## Status

- No pretrained weights are bundled or downloaded by the standard setup or CI.
- Mock adapters perform no real detection or recognition and are clearly labeled.
- Real adapters (`arcface`, `grounding_dino`) are disabled by default and raise a
  clear error if their optional dependencies are missing; they are never silently
  substituted by mocks.

## Facial similarity (Phase 3)

- DeepFace (library): MIT License. Source: https://github.com/serengil/deepface
- ArcFace (recognition model): verify the specific pretrained checkpoint's license
  and permitted use before deployment. The method originates from InsightFace.
- RetinaFace (detector): verify the specific detector/checkpoint license.

Pretrained face-recognition checkpoints are frequently restricted to
non-commercial or research use. Commercial deployment requires confirming the
exact weight files and their terms.

## Clothing detection (Phase 4)

- Grounding DINO (code): Apache-2.0. Source: https://github.com/IDEA-Research/GroundingDINO
- Grounding DINO pretrained weights: confirm the checkpoint license and any
  dataset-derived use restrictions before deployment.

## Record linkage (Phase 5)

- Splink: MIT License. Source: https://github.com/moj-analytical-services/splink
  Evaluated as a probabilistic baseline; see the matching documentation.

## Action items before real/commercial use

1. Record the exact checkpoint files and versions to be used.
2. Confirm each checkpoint's license permits the intended use.
3. Document data provenance and any dataset license constraints.
4. Re-run evaluation on licensed, consented data and record measured performance.
