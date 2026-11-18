from typing import Literal
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from .db import SessionLocal
from .core.settings import Settings
from .services.image_storage import LocalImageStorage
from .models import Incident, MissingPersonReport, PatientRecord, MatchCandidate
from .schemas import IncidentOut, DemoOverview
from .api import auth_routes, reports, patients, images, ai_routes

# Seeded synthetic scenario records use these id prefixes. The public dashboard
# counts only these so that authenticated demo intake never leaks live
# operational totals into the unauthenticated view.
SCENARIO_INCIDENT = 'INC-DEMO-'
SCENARIO_REPORT = 'M-DEMO-'
SCENARIO_PATIENT = 'H-DEMO-'
SCENARIO_CANDIDATE = 'C-DEMO-'


def create_app(session_factory=SessionLocal, settings: Settings | None = None, storage=None):
    settings = settings or Settings.from_env()
    storage = storage or LocalImageStorage(settings.upload_dir)

    app = FastAPI(
        title='Reunify — Synthetic Demo API',
        version='0.2.0',
        description='Synthetic disaster-reunification demo. Public routes expose generated '
                    'scenario totals only. Intake and tracking require development-only demo '
                    'authentication and never perform identity verification or inference.',
    )
    app.state.session_factory = session_factory
    app.state.settings = settings
    app.state.storage = storage

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'DELETE', 'OPTIONS'],
        allow_headers=['content-type', 'x-reunify-csrf'],
    )

    @app.get('/api/v1/health')
    def health():
        return {'status': 'ok', 'demo_only': True}

    @app.get('/api/v1/incidents', response_model=list[IncidentOut])
    def list_incidents(q: str = Query('', max_length=100), status: Literal['active', 'closed'] | None = None):
        statement = select(Incident).where(Incident.id.startswith(SCENARIO_INCIDENT)).order_by(
            Incident.start_time.desc(), Incident.id)
        if q.strip():
            statement = statement.where(Incident.name.icontains(q.strip(), autoescape=True) |
                                        Incident.affected_region.icontains(q.strip(), autoescape=True))
        if status:
            statement = statement.where(Incident.status == status)
        with session_factory() as db:
            return list(db.scalars(statement).all())

    @app.get('/api/v1/demo/overview', response_model=DemoOverview)
    def demo_overview():
        with session_factory() as db:
            def count(model, *conditions):
                return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0
            return DemoOverview(
                incident_count=count(Incident, Incident.id.startswith(SCENARIO_INCIDENT),
                                     Incident.status == 'active'),
                missing_reports=count(MissingPersonReport,
                                      MissingPersonReport.id.startswith(SCENARIO_REPORT)),
                hospital_records=count(PatientRecord, PatientRecord.id.startswith(SCENARIO_PATIENT)),
                suggested_matches=count(MatchCandidate, MatchCandidate.id.startswith(SCENARIO_CANDIDATE)),
                candidates_needing_review=count(MatchCandidate,
                                                MatchCandidate.id.startswith(SCENARIO_CANDIDATE),
                                                MatchCandidate.status == 'needs_review'),
                verified_resolutions=count(MissingPersonReport,
                                           MissingPersonReport.id.startswith(SCENARIO_REPORT),
                                           MissingPersonReport.status == 'verified'),
            )

    app.include_router(auth_routes.router)
    app.include_router(reports.router)
    app.include_router(patients.router)
    app.include_router(images.router)
    app.include_router(ai_routes.router)
    return app


app = create_app()
