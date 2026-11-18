# Matching evaluation

The matching engine is measured offline on synthetic, labeled data with no real
records. The harness lives in `backend/app/eval/` and is reproducible:

```
cd backend
python -m app.eval.evaluate_matching
```

## Methodology

- `synthetic.py` generates fictional persons, each producing one missing-person
  report and one unidentified-patient record with noisily perturbed attributes,
  plus unmatched distractor patients per incident.
- Train and test splits are **disjoint by both person and incident** (asserted in
  the harness and in `tests/test_evaluation.py`), so no person or incident appears
  in more than one split. The engine is a fixed heuristic with no learned
  parameters, so no fitting occurs; the split is maintained so the same harness
  applies when a learned model (Splink) is evaluated later.
- Metrics are computed only on the test split.

## Measured results

Measured on 2026-11-17 with the default configuration (seed 2026, 120 persons,
6 incidents, 10 distractors per incident, k=5). Numbers come from the harness
output, not hand-written estimates; rerun the command to reproduce.

| Metric | Value |
| --- | --- |
| Test reports | 120 |
| Test patient records | 180 |
| Recall@5 | 1.00 |
| Top-1 false-match rate | 0.133 |
| Reviewer burden (candidates surfaced per report) | 19.65 |
| Mean evidence score, true pairs | 3.875 |
| Mean evidence score, non-matching pairs | -0.295 |

## Interpretation and limitations

- **Recall@5 is high** on this synthetic distribution: the true patient is almost
  always among the top five suggestions.
- **Top-1 is not reliable on its own** (~13% of top-ranked suggestions are wrong),
  which is exactly why a human must investigate and independently verify.
- **Reviewer burden is high**: the engine deliberately surfaces every candidate
  with any supporting evidence, so reviewers see ~20 candidates per report on this
  synthetic set. This is a precision/recall trade-off to avoid missing true matches;
  tightening it is future work (e.g. a learned threshold or Splink weighting).
- The **score separates** true from non-matching pairs on average, but the score is
  an evidence tally, **not a calibrated probability**. Calibration metrics apply
  only to a future probabilistic model and are intentionally not reported here.
- These numbers describe a **synthetic distribution only** and do not predict
  real-world accuracy. No real evaluation has been performed and none is authorized.
