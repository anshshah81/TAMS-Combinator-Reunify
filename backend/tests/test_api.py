from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import func, inspect, select
from sqlalchemy.orm import sessionmaker
from app.db import make_engine
from app.main import create_app
from app.models import Incident, MissingPersonReport, PatientRecord, MatchCandidate
from app.seed import seed_synthetic_demo


@pytest.fixture()
def database(tmp_path):
    url = f"sqlite:///{(tmp_path / 'test.sqlite3').as_posix()}"
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    config.attributes['database_url'] = url
    command.upgrade(config, 'head')
    engine = make_engine(url)
    factory = sessionmaker(bind=engine)
    yield factory, config, engine
    engine.dispose()


@pytest.fixture()
def client(database):
    factory, _, _ = database
    with factory() as db:
        seed_synthetic_demo(db)
    with TestClient(create_app(factory)) as client:
        yield client


def test_health_endpoint(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'demo_only': True}


def test_synthetic_dashboard_data(client):
    assert client.get('/api/v1/demo/overview').json() == {
        'demo_only': True, 'incident_count': 1, 'missing_reports': 2,
        'hospital_records': 2, 'suggested_matches': 1,
        'candidates_needing_review': 1, 'verified_resolutions': 0,
    }
    incidents = client.get('/api/v1/incidents').json()
    assert [i['id'] for i in incidents] == ['INC-DEMO-001', 'INC-DEMO-002']
    assert set(incidents[0]) == {'id', 'name', 'disaster_type', 'affected_region', 'status', 'start_time'}


@pytest.mark.parametrize('query, expected', [
    ('status=active', ['INC-DEMO-001']), ('status=closed', ['INC-DEMO-002']),
    ('q=COAST', ['INC-DEMO-002']), ('q=Texas&status=active', ['INC-DEMO-001']),
    ('q=not-found', []), ('q=%25', []), ('q=_', []),
])
def test_incident_filters(client, query, expected):
    response = client.get(f'/api/v1/incidents?{query}')
    assert response.status_code == 200
    assert [i['id'] for i in response.json()] == expected


def test_filter_validation(client):
    assert client.get('/api/v1/incidents', params={'status': 'unknown'}).status_code == 422
    assert client.get('/api/v1/incidents', params={'q': 'a' * 101}).status_code == 422


def test_empty_database(database):
    with TestClient(create_app(database[0])) as client:
        assert client.get('/api/v1/incidents').json() == []
        overview = client.get('/api/v1/demo/overview').json()
        assert all(value == 0 for key, value in overview.items() if key != 'demo_only')


def test_seed_is_idempotent(database):
    with database[0]() as db:
        seed_synthetic_demo(db)
        seed_synthetic_demo(db)
        for model, expected in [(Incident, 2), (MissingPersonReport, 2), (PatientRecord, 2), (MatchCandidate, 1)]:
            assert db.scalar(select(func.count()).select_from(model)) == expected
        assert db.scalar(select(MatchCandidate)).ranking_score is None


def test_seed_preserves_existing_database(database):
    with database[0]() as db:
        seed_synthetic_demo(db)
        db.get(Incident, 'INC-DEMO-001').name = 'Edited exercise'
        db.commit()
        seed_synthetic_demo(db)
        assert db.get(Incident, 'INC-DEMO-001').name == 'Edited exercise'


def test_migration_round_trip(database):
    _, config, engine = database
    assert 'incidents' in inspect(engine).get_table_names()
    command.check(config)
    command.downgrade(config, 'base')
    assert 'incidents' not in inspect(engine).get_table_names()
    command.upgrade(config, 'head')
    assert 'incidents' in inspect(engine).get_table_names()


@pytest.mark.parametrize('path', ['patients', 'reports', 'matches', 'images', 'decisions'])
def test_restricted_routes_not_exposed(client, path):
    assert client.get(f'/api/v1/{path}').status_code == 404
    assert client.post(f'/api/v1/{path}', json={}).status_code == 404


def test_cors_allows_local_frontend_only(client):
    response = client.get('/api/v1/health', headers={'Origin': 'http://localhost:3000'})
    assert response.headers['access-control-allow-origin'] == 'http://localhost:3000'
    response = client.get('/api/v1/health', headers={'Origin': 'https://untrusted.example'})
    assert 'access-control-allow-origin' not in response.headers


def test_openapi_only_exposes_public_demo_routes(client):
    assert set(client.get('/openapi.json').json()['paths']) == {
        '/api/v1/health', '/api/v1/incidents', '/api/v1/demo/overview',
    }
