"""Measure the transparent matching engine on a synthetic, leakage-free split.

Metrics are computed on a test split whose persons and incidents are disjoint
from the (unused, since the engine is a fixed heuristic) train split. The engine
has no learned parameters, so no fitting occurs; the split is maintained so the
same harness works when a learned model (Splink) is evaluated later.

Run:  python -m app.eval.evaluate_matching
Reported numbers are measured from this run, never hand-written.
"""
from __future__ import annotations

import argparse
import json

from .synthetic import Dataset, generate_split
from ..services.ai.match_engine import rank_candidates


def _evaluate(dataset: Dataset, k: int) -> dict:
    total = len(dataset.reports)
    hits_at_k = 0
    top1_correct = 0
    top1_predictions = 0
    surfaced_counts: list[int] = []
    true_scores: list[int] = []
    false_scores: list[int] = []

    for report in dataset.reports:
        pool = dataset.patients_in(report.incident_id)
        ranked = rank_candidates(report, pool)
        surfaced_counts.append(len(ranked))
        ranked_ids = [patient.id for patient, _ in ranked]
        true_id = f'P-{report.person_id}'

        if true_id in ranked_ids[:k]:
            hits_at_k += 1
        if ranked:
            top1_predictions += 1
            top_patient, _ = ranked[0]
            if top_patient.id == true_id:
                top1_correct += 1
        for patient, evidence in ranked:
            (true_scores if patient.id == true_id else false_scores).append(evidence.score)

    reviewer_burden = sum(surfaced_counts) / total if total else 0.0
    return {
        'test_reports': total,
        'test_patients': len(dataset.patients),
        f'recall_at_{k}': round(hits_at_k / total, 4) if total else 0.0,
        'top1_false_match_rate': round(1 - top1_correct / top1_predictions, 4) if top1_predictions else None,
        'reviewer_burden_candidates_per_report': round(reviewer_burden, 3),
        'score_separation': {
            'mean_true_score': round(sum(true_scores) / len(true_scores), 3) if true_scores else None,
            'mean_false_score': round(sum(false_scores) / len(false_scores), 3) if false_scores else None,
            'note': 'Scores are an evidence tally, not calibrated probabilities; '
                    'calibration applies only to a future probabilistic model.',
        },
    }


def run(seed: int = 2026, persons: int = 120, incidents: int = 6,
        distractors_per_incident: int = 10, k: int = 5) -> dict:
    # Train split exists for methodology/leakage-safety; the heuristic uses no fitting.
    train = generate_split(seed=seed, persons=persons, incidents=incidents,
                           distractors_per_incident=distractors_per_incident)
    test = generate_split(seed=seed + 1, persons=persons, incidents=incidents,
                          distractors_per_incident=distractors_per_incident)
    train_persons = {report.person_id for report in train.reports}
    test_persons = {report.person_id for report in test.reports}
    train_incidents = {report.incident_id for report in train.reports}
    test_incidents = {report.incident_id for report in test.reports}
    assert train_persons.isdisjoint(test_persons), 'person leakage across splits'
    assert train_incidents.isdisjoint(test_incidents), 'incident leakage across splits'

    metrics = _evaluate(test, k)
    metrics['config'] = {
        'engine_version': rank_candidates.__module__,
        'seed': seed, 'persons': persons, 'incidents': incidents,
        'distractors_per_incident': distractors_per_incident, 'k': k,
        'splits': 'train/test disjoint by person and incident',
    }
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--persons', type=int, default=120)
    parser.add_argument('--incidents', type=int, default=6)
    parser.add_argument('--distractors', type=int, default=10)
    parser.add_argument('--k', type=int, default=5)
    args = parser.parse_args()
    metrics = run(seed=args.seed, persons=args.persons, incidents=args.incidents,
                  distractors_per_incident=args.distractors, k=args.k)
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
