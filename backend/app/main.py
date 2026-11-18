from typing import Literal
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from .db import SessionLocal
from .models import Incident, MissingPersonReport, PatientRecord, MatchCandidate
from .schemas import IncidentOut, DemoOverview


def create_app(session_factory=SessionLocal):
    app = FastAPI(title='Reunify — Synthetic Demo API', version='0.1.0',
                  description='Public synthetic exercise totals only. No intake, identity verification, or inference endpoints.')
    app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:3000'],
                       allow_credentials=False, allow_methods=['GET'], allow_headers=['*'])

    @app.get('/api/v1/health')
    def health():
        return {'status': 'ok', 'demo_only': True}

    @app.get('/api/v1/incidents', response_model=list[IncidentOut])
    def list_incidents(q: str = Query('', max_length=100), status: Literal['active', 'closed'] | None = None):
        statement = select(Incident).order_by(Incident.start_time.desc(), Incident.id)
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
                incident_count=count(Incident, Incident.status == 'active'),
                missing_reports=count(MissingPersonReport),
                hospital_records=count(PatientRecord),
                suggested_matches=count(MatchCandidate),
                candidates_needing_review=count(MatchCandidate, MatchCandidate.status == 'needs_review'),
                verified_resolutions=count(MissingPersonReport, MissingPersonReport.status == 'verified'),
            )
    return app


app = create_app()
