"""Phase 2 tests: development-only demo auth, role/ownership boundaries,
intake persistence, image handling, and migration-from-Phase-1 behavior."""
import io
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import select, text
from sqlalchemy.orm import sessionmaker

from app.core.settings import Settings
from app.db import make_engine
from app.main import create_app
from app.models import AuthSession, MissingPersonReport, User
from app.seed import seed_synthetic_demo
from app.seed_accounts import seed_demo_accounts
from app.services.image_storage import LocalImageStorage

CSRF = {'x-reunify-csrf': '1'}
REPORT = {
    'incident_id': 'INC-DEMO-001',
    'name': 'Test Person (synthetic)',
    'last_seen_location': 'Synthetic Town',
    'last_seen_time': '2026-06-02T10:00:00+00:00',
    'reporter_contact': 'demo-contact@example.invalid',
    'consent': True,
}
PATIENT = {'incident_id': 'INC-DEMO-001', 'internal_id': 'WARD-7-BED-3', 'consent': True}


def png_bytes(color=(200, 30, 30), size=(8, 8)) -> bytes:
    buffer = io.BytesIO()
    Image.new('RGB', size, color).save(buffer, format='PNG')
    return buffer.getvalue()


def build(tmp_path, **settings_kwargs):
    tmp_path = Path(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{(tmp_path / 'test.sqlite3').as_posix()}"
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    config.attributes['database_url'] = url
    command.upgrade(config, 'head')
    engine = make_engine(url)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        seed_synthetic_demo(db)
        seed_demo_accounts(db)
    kwargs = dict(environment='development', demo_auth=True, upload_dir=tmp_path / 'uploads')
    kwargs.update(settings_kwargs)
    settings = Settings(**kwargs)
    storage = LocalImageStorage(tmp_path / 'uploads')
    return create_app(factory, settings, storage), factory, engine


@pytest.fixture()
def env(tmp_path):
    app, factory, engine = build(tmp_path)
    yield app, factory
    engine.dispose()


def make_client(app, user_id=None):
    client = TestClient(app)
    if user_id:
        response = client.post('/api/v1/auth/login', json={'user_id': user_id}, headers=CSRF)
        assert response.status_code == 200, response.text
    return client


# --- Authentication ---------------------------------------------------------

def test_login_me_logout_cycle(env):
    app, _ = env
    client = make_client(app)
    assert client.get('/api/v1/auth/me').status_code == 401
    login = client.post('/api/v1/auth/login', json={'user_id': 'family-demo'}, headers=CSRF)
    assert login.status_code == 200
    assert login.json()['role'] == 'family'
    me = client.get('/api/v1/auth/me')
    assert me.status_code == 200 and me.json()['id'] == 'family-demo'
    assert client.post('/api/v1/auth/logout', headers=CSRF).status_code == 200
    assert client.get('/api/v1/auth/me').status_code == 401


def test_login_requires_csrf_and_known_account(env):
    app, _ = env
    client = TestClient(app)
    assert client.post('/api/v1/auth/login', json={'user_id': 'family-demo'}).status_code == 403
    bad_origin = client.post('/api/v1/auth/login', json={'user_id': 'family-demo'},
                             headers={**CSRF, 'origin': 'http://evil.example'})
    assert bad_origin.status_code == 403
    unknown = client.post('/api/v1/auth/login', json={'user_id': 'nope'}, headers=CSRF)
    assert unknown.status_code == 401


def test_expired_session_is_rejected(env):
    app, factory = env
    client = make_client(app, 'reviewer-demo')
    with factory() as db:
        session = db.scalars(select(AuthSession)).one()
        session.expires_at = session.expires_at.replace(year=2000)
        db.commit()
    assert client.get('/api/v1/auth/me').status_code == 401


def test_deactivated_user_is_rejected(env):
    app, factory = env
    client = make_client(app, 'family-demo')
    with factory() as db:
        db.get(User, 'family-demo').active = False
        db.commit()
    assert client.get('/api/v1/auth/me').status_code == 401


def test_demo_auth_disabled_denies_everything(tmp_path):
    app, _, engine = build(tmp_path, demo_auth=False)
    try:
        client = TestClient(app)
        for path in ('/api/v1/auth/me', '/api/v1/auth/demo-accounts',
                     '/api/v1/reports', '/api/v1/patients'):
            assert client.get(path).status_code == 503
        assert client.post('/api/v1/auth/login', json={'user_id': 'family-demo'},
                           headers=CSRF).status_code == 503
    finally:
        engine.dispose()


def test_demo_auth_rejected_outside_development(tmp_path):
    with pytest.raises(ValueError):
        Settings(environment='production', demo_auth=True)


# --- Family reports ---------------------------------------------------------

def test_family_creates_and_tracks_own_report(env):
    app, _ = env
    client = make_client(app, 'family-demo')
    created = client.post('/api/v1/reports', json=REPORT, headers=CSRF)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body['id'].startswith('MPR-') and body['status'] == 'received'
    tracking = client.get(f"/api/v1/reports/{body['id']}/tracking")
    assert tracking.status_code == 200
    assert set(tracking.json()) == {'id', 'status', 'created_at'}


def test_report_validation(env):
    app, _ = env
    client = make_client(app, 'family-demo')
    assert client.post('/api/v1/reports', json={**REPORT, 'consent': False}, headers=CSRF).status_code == 422
    assert client.post('/api/v1/reports', json={**REPORT, 'incident_id': 'INC-NOPE'}, headers=CSRF).status_code == 400
    no_name = {k: v for k, v in REPORT.items() if k != 'name'}
    assert client.post('/api/v1/reports', json=no_name, headers=CSRF).status_code == 422
    future = {**REPORT, 'last_seen_time': '2099-01-01T00:00:00+00:00'}
    assert client.post('/api/v1/reports', json=future, headers=CSRF).status_code == 422


def test_reports_are_isolated_per_owner(env):
    app, _ = env
    owner = make_client(app, 'family-demo')
    other = make_client(app, 'family-other')
    report_id = owner.post('/api/v1/reports', json=REPORT, headers=CSRF).json()['id']
    assert [r['id'] for r in owner.get('/api/v1/reports').json()] == [report_id]
    assert other.get('/api/v1/reports').json() == []
    assert other.get(f'/api/v1/reports/{report_id}/tracking').status_code == 404


def test_non_family_cannot_create_reports(env):
    app, _ = env
    client = make_client(app, 'hospital-demo')
    assert client.post('/api/v1/reports', json=REPORT, headers=CSRF).status_code == 403


def test_intake_does_not_leak_into_public_overview(env):
    app, _ = env
    client = make_client(app, 'family-demo')
    before = client.get('/api/v1/demo/overview').json()
    client.post('/api/v1/reports', json=REPORT, headers=CSRF)
    after = client.get('/api/v1/demo/overview').json()
    assert before == after and after['missing_reports'] == 2


# --- Hospital patients ------------------------------------------------------

def test_hospital_creates_patient_with_server_derived_org(env):
    app, _ = env
    client = make_client(app, 'hospital-demo')
    created = client.post('/api/v1/patients', json=PATIENT, headers=CSRF)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body['id'].startswith('PAT-')
    assert body['organization_id'] == 'SYNTH-HOSPITAL-1'


def test_patient_body_cannot_override_organization(env):
    app, _ = env
    client = make_client(app, 'hospital-demo')
    payload = {**PATIENT, 'organization_id': 'SYNTH-HOSPITAL-2'}
    assert client.post('/api/v1/patients', json=payload, headers=CSRF).status_code == 422


def test_duplicate_internal_id_conflicts(env):
    app, _ = env
    client = make_client(app, 'hospital-demo')
    assert client.post('/api/v1/patients', json=PATIENT, headers=CSRF).status_code == 201
    assert client.post('/api/v1/patients', json=PATIENT, headers=CSRF).status_code == 409
    other = {**PATIENT, 'internal_id': 'WARD-7-BED-4'}
    assert client.post('/api/v1/patients', json=other, headers=CSRF).status_code == 201


def test_patients_isolated_by_organization(env):
    app, _ = env
    hospital_a = make_client(app, 'hospital-demo')
    hospital_b = make_client(app, 'hospital-other')
    created = hospital_a.post('/api/v1/patients', json=PATIENT, headers=CSRF).json()
    assert [p['id'] for p in hospital_a.get('/api/v1/patients').json()] == [created['id']]
    assert hospital_b.get('/api/v1/patients').json() == []
    assert hospital_b.get(f"/api/v1/patients/{created['id']}").status_code == 404


def test_reviewer_and_admin_can_read_patients(env):
    app, _ = env
    created = make_client(app, 'hospital-demo').post('/api/v1/patients', json=PATIENT, headers=CSRF).json()
    for role_user in ('reviewer-demo', 'admin-demo'):
        client = make_client(app, role_user)
        assert any(p['id'] == created['id'] for p in client.get('/api/v1/patients').json())
        assert client.get(f"/api/v1/patients/{created['id']}").status_code == 200


def test_family_cannot_access_patients(env):
    app, _ = env
    client = make_client(app, 'family-demo')
    assert client.get('/api/v1/patients').status_code == 403
    assert client.post('/api/v1/patients', json=PATIENT, headers=CSRF).status_code == 403


# --- Images -----------------------------------------------------------------

def test_image_upload_attach_and_authorized_retrieval(env):
    app, _ = env
    family = make_client(app, 'family-demo')
    upload = family.post('/api/v1/images', files={'file': ('p.png', png_bytes(), 'image/png')}, headers=CSRF)
    assert upload.status_code == 200, upload.text
    image_id = upload.json()['image_id']
    assert len(image_id) == 32
    created = family.post('/api/v1/reports', json={**REPORT, 'image_id': image_id}, headers=CSRF)
    assert created.status_code == 201
    mine = family.get(f'/api/v1/images/{image_id}')
    assert mine.status_code == 200 and mine.headers['content-type'] == 'image/png'
    # A different family account cannot read it; a reviewer can.
    assert make_client(app, 'family-other').get(f'/api/v1/images/{image_id}').status_code == 404
    assert make_client(app, 'reviewer-demo').get(f'/api/v1/images/{image_id}').status_code == 200


def test_invalid_and_oversized_images_rejected(env, tmp_path):
    app, _ = env
    family = make_client(app, 'family-demo')
    bad = family.post('/api/v1/images', files={'file': ('x.png', b'not an image', 'image/png')}, headers=CSRF)
    assert bad.status_code == 400
    small_app, _, engine = build(tmp_path / 'small', max_image_bytes=50)
    try:
        client = make_client(small_app, 'family-demo')
        big = client.post('/api/v1/images', files={'file': ('p.png', png_bytes(), 'image/png')}, headers=CSRF)
        assert big.status_code == 413
    finally:
        engine.dispose()


def test_reviewer_cannot_upload_intake_images(env):
    app, _ = env
    client = make_client(app, 'reviewer-demo')
    response = client.post('/api/v1/images', files={'file': ('p.png', png_bytes(), 'image/png')}, headers=CSRF)
    assert response.status_code == 403


def test_cannot_reuse_or_steal_another_users_image(env):
    app, _ = env
    family = make_client(app, 'family-demo')
    image_id = family.post('/api/v1/images', files={'file': ('p.png', png_bytes(), 'image/png')},
                           headers=CSRF).json()['image_id']
    assert family.post('/api/v1/reports', json={**REPORT, 'image_id': image_id}, headers=CSRF).status_code == 201
    # Reusing an already-attached image is rejected.
    assert family.post('/api/v1/reports', json={**REPORT, 'image_id': image_id}, headers=CSRF).status_code == 400
    # Another user cannot attach an image they do not own.
    other_image = make_client(app, 'family-other').post(
        '/api/v1/images', files={'file': ('p.png', png_bytes(), 'image/png')}, headers=CSRF).json()['image_id']
    assert family.post('/api/v1/reports', json={**REPORT, 'image_id': other_image}, headers=CSRF).status_code == 400


# --- Migration from Phase 1 data -------------------------------------------

def test_consent_backfills_existing_rows(tmp_path):
    url = f"sqlite:///{(tmp_path / 'legacy.sqlite3').as_posix()}"
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    config.attributes['database_url'] = url
    command.upgrade(config, '059fe07f326f')
    engine = make_engine(url, enforce_foreign_keys=False)
    with engine.begin() as connection:
        connection.execute(text(
            'INSERT INTO incidents (id, name, disaster_type, affected_region, status, start_time) '
            "VALUES ('INC-LEGACY', 'Legacy', 'flood', 'region', 'active', '2026-01-01 00:00:00')"))
        connection.execute(text(
            'INSERT INTO missing_person_reports (id, incident_id, name, status, created_at) '
            "VALUES ('M-LEGACY', 'INC-LEGACY', 'Legacy person', 'received', '2026-01-01 00:00:00')"))
    engine.dispose()
    command.upgrade(config, 'head')
    runtime = make_engine(url)
    with sessionmaker(bind=runtime)() as db:
        report = db.get(MissingPersonReport, 'M-LEGACY')
        assert report.consent is False
        assert report.owner_id is None
    runtime.dispose()
