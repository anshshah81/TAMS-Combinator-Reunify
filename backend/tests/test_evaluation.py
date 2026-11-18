"""Phase 7 tests: the offline evaluation harness is leakage-free and reports
the expected metric shape on synthetic data."""
from app.eval.evaluate_matching import run
from app.eval.synthetic import generate_split


def test_splits_are_disjoint_by_person_and_incident():
    a = generate_split(seed=1, persons=20, incidents=4, distractors_per_incident=3)
    b = generate_split(seed=2, persons=20, incidents=4, distractors_per_incident=3)
    a_persons = {record.person_id for record in a.reports}
    b_persons = {record.person_id for record in b.reports}
    a_incidents = {record.incident_id for record in a.reports}
    b_incidents = {record.incident_id for record in b.reports}
    assert a_persons.isdisjoint(b_persons)
    assert a_incidents.isdisjoint(b_incidents)


def test_run_reports_expected_metrics():
    metrics = run(seed=7, persons=40, incidents=4, distractors_per_incident=5, k=5)
    assert metrics['test_reports'] == 40
    assert 0.0 <= metrics['recall_at_5'] <= 1.0
    assert metrics['top1_false_match_rate'] is None or 0.0 <= metrics['top1_false_match_rate'] <= 1.0
    assert metrics['reviewer_burden_candidates_per_report'] >= 0
    # True matches should, on average, score above non-matches.
    separation = metrics['score_separation']
    assert separation['mean_true_score'] > separation['mean_false_score']
