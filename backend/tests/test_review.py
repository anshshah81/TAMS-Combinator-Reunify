"""Phase 6 tests: investigation view, human decision workflow, status
transitions, immutable audit, admin management, and access restrictions.

A verification can only be recorded by a human reviewer with an attestation;
the AI/matching pipeline never produces a verified status or contacts families.
"""
from app.models import MatchCandidate, MissingPersonReport

from test_intake import CSRF, build, make_client  # shared Phase 2 harness

CANDIDATE = 'C-DEMO-301'  # seeded M-DEMO-101 <-> H-DEMO-201 candidate
VERIFY = {'decision': 'verify', 'notes': 'Independent documents match.',
          'attestation': 'I verified identity using government ID and next-of-kin confirmation.'}


def _seed_candidates(app):
    reviewer = make_client(app, 'reviewer-demo')
    assert reviewer.post('/api/v1/incidents/INC-DEMO-001/candidates', headers=CSRF).status_code == 200
    return reviewer


def test_investigation_view_and_decision_flow(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        reviewer = _seed_candidates(app)
        view = reviewer.get(f'/api/v1/match-candidates/{CANDIDATE}/investigation')
        assert view.status_code == 200, view.text
        body = view.json()
        assert body['report']['name'].startswith('Jordan Reed')
        assert body['patient']['id'] == 'H-DEMO-201'
        assert body['evidence']['supporting']

        investigate = reviewer.post(f'/api/v1/match-candidates/{CANDIDATE}/decisions',
                                    json={'decision': 'investigate', 'notes': 'Looks plausible.'},
                                    headers=CSRF)
        assert investigate.status_code == 201, investigate.text
        assert investigate.json()['new_status'] == 'investigating'

        # Verification requires both notes and an attestation.
        assert reviewer.post(f'/api/v1/match-candidates/{CANDIDATE}/decisions',
                             json={'decision': 'verify', 'notes': 'done'}, headers=CSRF).status_code == 422

        verified = reviewer.post(f'/api/v1/match-candidates/{CANDIDATE}/decisions',
                                 json=VERIFY, headers=CSRF)
        assert verified.status_code == 201, verified.text
        assert verified.json()['new_status'] == 'verified'

        # A finalized candidate rejects further decisions.
        again = reviewer.post(f'/api/v1/match-candidates/{CANDIDATE}/decisions',
                              json={'decision': 'reject', 'notes': 'n/a'}, headers=CSRF)
        assert again.status_code == 409

        history = reviewer.get(f'/api/v1/match-candidates/{CANDIDATE}/decisions').json()
        assert [d['decision'] for d in history][:2] == ['verify', 'investigate']
    finally:
        engine.dispose()


def test_verify_updates_report_status_and_writes_audit(tmp_path):
    app, factory, engine = build(tmp_path)
    try:
        _seed_candidates(app)
        reviewer = make_client(app, 'reviewer-demo')
        assert reviewer.post(f'/api/v1/match-candidates/{CANDIDATE}/decisions',
                             json=VERIFY, headers=CSRF).status_code == 201
        with factory() as db:
            candidate = db.get(MatchCandidate, CANDIDATE)
            report = db.get(MissingPersonReport, candidate.missing_person_id)
            assert candidate.status == 'verified'
            assert report.status == 'resolved'  # coarse, detail-free family projection

        admin = make_client(app, 'admin-demo')
        actions = {entry['action'] for entry in admin.get('/api/v1/admin/audit-logs').json()}
        assert {'candidate.verify', 'identity.verified'} <= actions
    finally:
        engine.dispose()


def test_investigate_moves_report_under_review(tmp_path):
    app, factory, engine = build(tmp_path)
    try:
        _seed_candidates(app)
        reviewer = make_client(app, 'reviewer-demo')
        reviewer.post(f'/api/v1/match-candidates/{CANDIDATE}/decisions',
                      json={'decision': 'investigate', 'notes': 'checking'}, headers=CSRF)
        with factory() as db:
            candidate = db.get(MatchCandidate, CANDIDATE)
            report = db.get(MissingPersonReport, candidate.missing_person_id)
            assert report.status == 'under_review'
    finally:
        engine.dispose()


def test_review_and_admin_access_restrictions(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        _seed_candidates(app)
        family = make_client(app, 'family-demo')
        hospital = make_client(app, 'hospital-demo')
        reviewer = make_client(app, 'reviewer-demo')

        # Family and hospital cannot investigate or decide.
        for client in (family, hospital):
            assert client.get(f'/api/v1/match-candidates/{CANDIDATE}/investigation').status_code == 403
            assert client.get(f'/api/v1/match-candidates/{CANDIDATE}/decisions').status_code == 403
            assert client.post(f'/api/v1/match-candidates/{CANDIDATE}/decisions',
                               json={'decision': 'reject', 'notes': 'x'}, headers=CSRF).status_code == 403

        # Admin-only surfaces are closed to reviewers and families.
        for client in (family, hospital, reviewer):
            assert client.get('/api/v1/admin/audit-logs').status_code == 403
            assert client.get('/api/v1/admin/users').status_code == 403
    finally:
        engine.dispose()


def test_admin_incident_management(tmp_path):
    app, _, engine = build(tmp_path)
    try:
        admin = make_client(app, 'admin-demo')
        ok = admin.patch('/api/v1/admin/incidents/INC-DEMO-001', json={'status': 'closed'}, headers=CSRF)
        assert ok.status_code == 200 and ok.json()['status'] == 'closed'
        assert admin.patch('/api/v1/admin/incidents/INC-NOPE', json={'status': 'closed'},
                           headers=CSRF).status_code == 404

        reviewer = make_client(app, 'reviewer-demo')
        assert reviewer.patch('/api/v1/admin/incidents/INC-DEMO-001', json={'status': 'active'},
                              headers=CSRF).status_code == 403
    finally:
        engine.dispose()
