"""Phase 5 tests: transparent matching evidence, ranking, no-match handling,
and the restricted matching API."""
from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.ai.match_engine import ENGINE_VERSION, evaluate_pair, rank_candidates

from test_intake import CSRF, build, make_client  # shared Phase 2 harness


def person(**kwargs):
    base = dict(approximate_age=None, height_cm=None, hair_color=None, eye_color=None,
                distinguishing_features=None, clothing_description=None, observed_clothing=None,
                last_seen_time=None, admission_time=None, internal_id=None, organization_id=None, id='x')
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_strong_pair_accumulates_supporting_evidence():
    report = person(approximate_age=26, height_cm=165, hair_color='dark',
                    distinguishing_features='small scar on left forearm',
                    clothing_description='red hoodie and blue jeans')
    patient = person(approximate_age=28, height_cm=166, hair_color='dark',
                     distinguishing_features='scar on left forearm', observed_clothing='blue jeans')
    evidence = evaluate_pair(report, patient)
    assert evidence.score > 0
    assert any('age' in item for item in evidence.supporting)
    assert any('hair color' in item for item in evidence.supporting)
    assert evidence.conflicting == []
    assert evidence.engine_version == ENGINE_VERSION


def test_conflicting_pair_scores_negative():
    report = person(approximate_age=20, height_cm=160, hair_color='blonde')
    patient = person(approximate_age=70, height_cm=185, hair_color='black')
    evidence = evaluate_pair(report, patient)
    assert evidence.score < 0
    assert any('age' in item for item in evidence.conflicting)
    assert any('hair color' in item for item in evidence.conflicting)


def test_missing_fields_are_missing_not_conflicting():
    evidence = evaluate_pair(person(), person())
    assert evidence.conflicting == []
    assert any('age' in item for item in evidence.missing)
    assert any('face comparison not run' in item for item in evidence.missing)
    assert any('unidentified' in item for item in evidence.missing)


def test_timeline_ordering_signals():
    report = person(last_seen_time=datetime(2026, 6, 1, tzinfo=timezone.utc))
    after = person(admission_time=datetime(2026, 6, 2, tzinfo=timezone.utc))
    before = person(admission_time=datetime(2026, 5, 20, tzinfo=timezone.utc))
    assert any('after the last-seen' in item for item in evaluate_pair(report, after).supporting)
    assert any('precedes the last-seen' in item for item in evaluate_pair(report, before).conflicting)


def test_rank_filters_unsupported_and_sorts():
    report = person(approximate_age=30, height_cm=170, hair_color='brown')
    good = person(id='good', approximate_age=31, height_cm=171, hair_color='brown')
    weak = person(id='weak', approximate_age=30, height_cm=250, hair_color='brown')  # one support, one conflict
    none = person(id='none', approximate_age=80, height_cm=120, hair_color='white')  # no support
    ranked = rank_candidates(report, [none, weak, good])
    ids = [patient.id for patient, _ in ranked]
    assert 'none' not in ids
    assert ids[0] == 'good'  # highest score first


def test_no_match_returns_empty():
    report = person(approximate_age=20, hair_color='blonde')
    patient = person(id='p', approximate_age=80, hair_color='black')
    assert rank_candidates(report, [patient]) == []


def test_face_distance_is_weak_evidence():
    report = person(approximate_age=30)
    patient = person(id='p', approximate_age=30)
    low = evaluate_pair(report, patient, face_distance=0.1)
    high = evaluate_pair(report, patient, face_distance=1.2)
    assert any('face distance' in item for item in low.supporting)
    assert any('face distance' in item for item in high.conflicting)


# --- Endpoint -----------------------------------------------------------------

def test_reviewer_generates_and_lists_candidates(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        reviewer = make_client(app, 'reviewer-demo')
        generated = reviewer.post('/api/v1/incidents/INC-DEMO-001/candidates', headers=CSRF)
        assert generated.status_code == 200, generated.text
        candidates = generated.json()
        assert candidates, 'expected at least one seeded-incident candidate'
        top = candidates[0]
        assert top['evidence']['supporting'] and top['ranking_score'] is not None
        # Listing returns persisted candidates with evidence.
        listed = reviewer.get('/api/v1/match-candidates?incident_id=INC-DEMO-001').json()
        assert any(c['missing_person_id'] == 'M-DEMO-101' for c in listed)
    finally:
        engine.dispose()


def test_generation_preserves_existing_status(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        reviewer = make_client(app, 'reviewer-demo')
        reviewer.post('/api/v1/incidents/INC-DEMO-001/candidates', headers=CSRF)
        # The seeded candidate C-DEMO-301 keeps its needs_review status after refresh.
        detail = reviewer.get('/api/v1/match-candidates/C-DEMO-301').json()
        assert detail['status'] == 'needs_review'
        assert detail['ranking_score'] is not None
    finally:
        engine.dispose()


def test_matching_denied_to_family_and_unknown_incident(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        family = make_client(app, 'family-demo')
        assert family.post('/api/v1/incidents/INC-DEMO-001/candidates', headers=CSRF).status_code == 403
        assert family.get('/api/v1/match-candidates').status_code == 403
        reviewer = make_client(app, 'reviewer-demo')
        assert reviewer.post('/api/v1/incidents/INC-NOPE/candidates', headers=CSRF).status_code == 404
    finally:
        engine.dispose()
